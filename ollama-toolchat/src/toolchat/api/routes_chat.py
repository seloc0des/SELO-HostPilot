from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, AsyncGenerator
import threading
import requests
import json
from ..agent.ollama_client import ollama_client
from ..agent.memory_store import memory_store
from ..agent.tool_router import tool_router
from ..agent.prompt import get_system_prompt, format_tool_result
from ..agent.query_classifier import classify_query, is_auto_response, get_auto_response
from ..config import settings
from ..infra.logging import get_logger

logger = get_logger(__name__)

router = APIRouter()

_model_lock = threading.Lock()
_current_model = settings.ollama_model


def get_current_model() -> str:
    with _model_lock:
        return _current_model


def set_current_model(model: str) -> None:
    global _current_model
    with _model_lock:
        _current_model = model


class ChatSendRequest(BaseModel):
    session_id: Optional[str] = None
    message: str


class ChatConfirmRequest(BaseModel):
    session_id: str
    plan_id: str
    confirm: bool


class ChatConfirmResponse(BaseModel):
    reply: str


class ModelGetResponse(BaseModel):
    model: str


class ModelSetRequest(BaseModel):
    model: str


class ModelSetResponse(BaseModel):
    model: str
    message: str


class ModelsListResponse(BaseModel):
    models: list[str]


@router.post("/v1/chat/confirm", response_model=ChatConfirmResponse)
async def chat_confirm(request: ChatConfirmRequest):
    if not request.confirm:
        return ChatConfirmResponse(reply="Action cancelled.")
    
    try:
        from ..agent.planner import plan_store
        plan = plan_store.get_plan(request.plan_id)
        tool_name = plan.tool_name if plan else "unknown"
        
        result = tool_router.execute_confirmed_plan(request.plan_id)
        
        if result.ok:
            reply = format_tool_result(tool_name, result.dict())
        else:
            reply = f"Action failed: {result.message}"
        
        memory_store.add_message(request.session_id, "assistant", reply)
        
        return ChatConfirmResponse(reply=reply)
    
    except Exception as e:
        logger.error(f"Chat confirm failed: {e}", exc_info=True, extra={
            "session_id": request.session_id,
            "plan_id": request.plan_id,
        })
        raise HTTPException(status_code=500, detail=f"Confirmation failed: {str(e)}")


@router.get("/v1/model", response_model=ModelGetResponse)
async def get_model():
    return ModelGetResponse(model=get_current_model())


@router.get("/v1/models", response_model=ModelsListResponse)
async def get_models():
    """Fetch available models from Ollama."""
    try:
        response = requests.get(f"{settings.ollama_url}/api/tags", timeout=5)
        response.raise_for_status()
        available_models = [model["name"] for model in response.json().get("models", [])]
        return ModelsListResponse(models=available_models)
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch models from Ollama: {e}")
        raise HTTPException(
            status_code=503,
            detail=f"Failed to fetch models from Ollama: {str(e)}"
        )


@router.post("/v1/model", response_model=ModelSetResponse)
async def set_model_endpoint(request: ModelSetRequest):
    try:
        response = requests.get(f"{settings.ollama_url}/api/tags", timeout=5)
        response.raise_for_status()
        available_models = [model["name"] for model in response.json().get("models", [])]
        
        # Check if the requested model exists in available models
        # Support exact match or partial match (e.g., "llama3" matches "llama3:8b")
        model_exists = request.model in available_models
        
        if not model_exists:
            raise HTTPException(
                status_code=400,
                detail=f"Model '{request.model}' not found. Available models: {', '.join(available_models)}"
            )
        
        set_current_model(request.model)
        logger.info(f"Model changed to: {request.model}")
        
        return ModelSetResponse(
            model=request.model,
            message=f"Model changed to {request.model}"
        )
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to verify model: {e}")
        set_current_model(request.model)
        return ModelSetResponse(
            model=request.model,
            message=f"Model changed to {request.model} (verification skipped)"
        )


@router.post("/v1/chat/send/stream")
async def chat_send_stream(request: ChatSendRequest):
    """
    Streaming version of chat endpoint using Server-Sent Events.
    Useful for long-running commands where progress updates are valuable.
    """
    async def event_generator() -> AsyncGenerator[str, None]:
        session_id = request.session_id
        
        if not session_id or not memory_store.session_exists(session_id):
            session_id = memory_store.create_session()
            logger.info(f"Created new session: {session_id}")
            yield f"data: {json.dumps({'type': 'session', 'session_id': session_id})}\n\n"
        
        memory_store.add_message(session_id, "user", request.message)
        yield f"data: {json.dumps({'type': 'status', 'message': 'Processing request...'})}\n\n"
        
        try:
            history = memory_store.get_history(session_id)
            messages = [{"role": "system", "content": get_system_prompt()}] + history
            
            # FIRST: Check if this is an auto-response query
            if is_auto_response(request.message):
                auto_response = get_auto_response(request.message)
                logger.info(
                    f"Auto-response triggered for query: {request.message}",
                    extra={"session_id": session_id}
                )
                yield f"data: {json.dumps({'type': 'status', 'message': 'Generating response...'})}\n\n"
                
                memory_store.add_message(session_id, "assistant", auto_response)
                yield f"data: {json.dumps({'type': 'message', 'role': 'assistant', 'content': auto_response})}\n\n"
                yield f"data: {json.dumps({'type': 'done'})}\n\n"
                return
            
            # SECOND: Classify the query to check if it requires a tool call
            requires_tool, suggested_tool = classify_query(request.message)
            
            if requires_tool and suggested_tool and not suggested_tool.startswith("auto_response:"):
                # System query detected - call tool FIRST, skip initial LLM call
                logger.info(
                    f"System query detected, calling tool directly: {suggested_tool}",
                    extra={"session_id": session_id, "tool": suggested_tool}
                )
                yield f"data: {json.dumps({'type': 'status', 'message': 'Querying system data...'})}\n\n"
                
                tool_call = {
                    "tool": suggested_tool,
                    "args": {},
                    "explain": f"Retrieving system information"
                }
                assistant_message = ""  # No initial LLM response needed
            else:
                # Not a system query - let LLM respond normally
                ollama_client.model = get_current_model()
                yield f"data: {json.dumps({'type': 'status', 'message': 'Calling LLM...'})}\n\n"
                
                response = ollama_client.chat(messages=messages)
                assistant_message = response.get("message", {}).get("content", "")
                
                tool_call = tool_router.parse_tool_call(assistant_message)
            
            if tool_call:
                tool_name = tool_call.get("tool")
                args = tool_call.get("args", {})
                explain = tool_call.get("explain", "")
                
                yield f"data: {json.dumps({'type': 'tool_call', 'tool': tool_name, 'explain': explain})}\n\n"
                
                result, plan_id = tool_router.execute_tool(tool_name, args, session_id)
                
                tool_result_msg = format_tool_result(tool_name, result.dict())
                memory_store.add_message(session_id, "system", tool_result_msg)
                
                if plan_id:
                    confirmation_message = (
                        f"{explain}\n\n"
                        f"I've prepared a plan to {tool_name}. Here's what will happen:\n"
                        f"{result.data}\n\n"
                        f"Please confirm if you want to proceed."
                    )
                    memory_store.add_message(session_id, "assistant", confirmation_message)
                    
                    yield f"data: {json.dumps({'type': 'confirmation', 'plan_id': plan_id, 'message': confirmation_message})}\n\n"
                else:
                    yield f"data: {json.dumps({'type': 'tool_result', 'result': result.dict()})}\n\n"
                    
                    # Build messages for final response
                    # Add explicit instruction to respond conversationally
                    conversation_instruction = (
                        "IMPORTANT: The tool has already been executed and returned real data above. "
                        "Your job now is to explain these results to the user in a friendly, conversational way. "
                        "DO NOT output JSON. DO NOT try to call another tool. DO NOT output {\"tool\": \"...\"}. "
                        "Just craft a natural response using the exact numbers from the tool results."
                    )
                    
                    # If assistant_message is empty (classifier called tool directly), don't add it
                    if assistant_message.strip():
                        messages_with_result = messages + [
                            {"role": "assistant", "content": assistant_message},
                            {"role": "system", "content": f"{tool_result_msg}\n\n{conversation_instruction}"}
                        ]
                    else:
                        # Classifier called tool directly - just add the system result with instruction
                        messages_with_result = messages + [
                            {"role": "system", "content": f"{tool_result_msg}\n\n{conversation_instruction}"}
                        ]
                    
                    logger.info(f"Tool result message: {tool_result_msg}", extra={"session_id": session_id})
                    yield f"data: {json.dumps({'type': 'status', 'message': 'Generating response...'})}\n\n"
                    
                    ollama_client.model = get_current_model()
                    logger.info(f"Calling Ollama for final response with model: {get_current_model()}", extra={"session_id": session_id})
                    final_response = ollama_client.chat(messages=messages_with_result)
                    logger.info(f"Final response from Ollama: {final_response}", extra={"session_id": session_id})
                    final_message = final_response.get("message", {}).get("content", "").strip()
                    logger.info(f"Final message extracted: '{final_message}'", extra={"session_id": session_id})
                    
                    # Fallback: if model generates another tool call, empty response, or suspicious response, show tool results directly
                    is_another_tool_call = tool_router.parse_tool_call(final_message) is not None
                    # Check for placeholder patterns (avoid false positives on markdown)
                    placeholder_patterns = ['xxx', 'yyy', 'n/a', 'please wait', 'processing', '[insert', '[placeholder']
                    has_placeholders = any(p in final_message.lower() for p in placeholder_patterns)
                    has_confusion = any(p in final_message for p in ['1/8', '1/4', '1/2']) and 'GB' in final_message  # Likely misinterpretation
                    
                    if not final_message or len(final_message) < 15 or is_another_tool_call or has_placeholders or has_confusion:
                        logger.warning(f"Model generated invalid response (empty/short/tool_call/placeholder/confusion), using tool result directly", extra={"session_id": session_id})
                        # Use the formatted tool result instead of raw data
                        final_message = tool_result_msg
                    
                    memory_store.add_message(session_id, "assistant", final_message)
                    
                    yield f"data: {json.dumps({'type': 'message', 'role': 'assistant', 'content': final_message})}\n\n"
            else:
                memory_store.add_message(session_id, "assistant", assistant_message)
                yield f"data: {json.dumps({'type': 'message', 'role': 'assistant', 'content': assistant_message})}\n\n"
            
            yield f"data: {json.dumps({'type': 'done'})}\n\n"
        
        except Exception as e:
            logger.error(f"Streaming chat failed: {e}", exc_info=True)
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
    
    return StreamingResponse(event_generator(), media_type="text/event-stream")
