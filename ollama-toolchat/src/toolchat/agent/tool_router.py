import json
import uuid
from typing import Dict, Any, Optional, Tuple
from ..tools.registry import registry
from ..tools.base import ToolResult
from .planner import plan_store
from ..infra.logging import get_logger
from ..infra.audit import audit_logger

logger = get_logger(__name__)


class ToolRouter:
    def parse_tool_call(self, response: str) -> Optional[Dict[str, Any]]:
        try:
            response = response.strip()
            
            # Handle code blocks
            if response.startswith("```"):
                lines = response.split("\n")
                json_lines = []
                in_code_block = False
                for line in lines:
                    if line.startswith("```"):
                        in_code_block = not in_code_block
                        continue
                    if in_code_block:
                        json_lines.append(line)
                response = "\n".join(json_lines)
            
            # Try to parse the entire response as JSON first
            try:
                tool_call = json.loads(response)
                if "tool" in tool_call and "args" in tool_call:
                    return tool_call
            except json.JSONDecodeError:
                pass
            
            # If that fails, try to extract JSON from mixed content
            # Look for JSON object pattern: {"tool": ...
            # This handles nested braces by counting brace depth
            start_idx = response.find('{"tool"')
            if start_idx == -1:
                start_idx = response.find('{ "tool"')  # Handle space after brace
            
            if start_idx != -1:
                # Find the matching closing brace
                brace_count = 0
                end_idx = -1
                for i in range(start_idx, len(response)):
                    if response[i] == '{':
                        brace_count += 1
                    elif response[i] == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            end_idx = i + 1
                            break
                
                if end_idx != -1:
                    json_str = response[start_idx:end_idx]
                    try:
                        tool_call = json.loads(json_str)
                        if "tool" in tool_call and "args" in tool_call:
                            return tool_call
                    except json.JSONDecodeError:
                        pass
            
            return None
        except Exception as e:
            logger.error(f"Failed to parse tool call: {e}")
            return None
    
    def execute_tool(
        self,
        tool_name: str,
        args: Dict[str, Any],
        session_id: str,
        dry_run: bool = False
    ) -> Tuple[ToolResult, Optional[str]]:
        request_id = str(uuid.uuid4())
        tool = registry.get(tool_name)
        
        if not tool:
            return ToolResult(
                ok=False,
                error_code="tool_not_found",
                message=f"Tool '{tool_name}' not found"
            ), None
        
        logger.info(f"Executing tool: {tool_name}", extra={
            "tool_name": tool_name,
            "tier": tool.spec.tier,
            "session_id": session_id,
            "request_id": request_id,
        })
        
        if tool.spec.requires_confirmation and not dry_run:
            result = tool.execute(args, dry_run=True)
            
            if result.ok:
                summary = f"Tool '{tool_name}' will perform: {result.data}"
                plan_id = plan_store.create_plan(session_id, tool_name, args, summary)
                
                audit_logger.log_tool_execution(
                    session_id=session_id,
                    request_id=request_id,
                    tool_name=tool_name,
                    tier=int(tool.spec.tier),
                    action="dry_run",
                    details=args,
                    result=result.dict(),
                    user_confirmed=False
                )
                
                return result, plan_id
            else:
                return result, None
        
        result = tool.execute(args, dry_run=dry_run)
        
        if not dry_run:
            audit_logger.log_tool_execution(
                session_id=session_id,
                request_id=request_id,
                tool_name=tool_name,
                tier=int(tool.spec.tier),
                action="execute",
                details=args,
                result=result.dict(),
                user_confirmed=False
            )
        
        return result, None
    
    def execute_confirmed_plan(self, plan_id: str) -> ToolResult:
        request_id = str(uuid.uuid4())
        plan = plan_store.get_plan(plan_id)
        
        if not plan:
            return ToolResult(
                ok=False,
                error_code="plan_not_found",
                message=f"Plan '{plan_id}' not found"
            )
        
        if plan.executed:
            return ToolResult(
                ok=False,
                error_code="plan_already_executed",
                message=f"Plan '{plan_id}' has already been executed"
            )
        
        tool = registry.get(plan.tool_name)
        if not tool:
            return ToolResult(
                ok=False,
                error_code="tool_not_found",
                message=f"Tool '{plan.tool_name}' not found"
            )
        
        logger.info(f"Executing confirmed plan: {plan_id}", extra={
            "plan_id": plan_id,
            "tool_name": plan.tool_name,
            "session_id": plan.session_id,
            "request_id": request_id,
        })
        
        result = tool.execute(plan.args, dry_run=False)
        plan_store.mark_executed(plan_id)
        
        audit_logger.log_tool_execution(
            session_id=plan.session_id,
            request_id=request_id,
            tool_name=plan.tool_name,
            tier=int(tool.spec.tier),
            action="execute_confirmed",
            details=plan.args,
            result=result.dict(),
            user_confirmed=True
        )
        
        return result


tool_router = ToolRouter()
