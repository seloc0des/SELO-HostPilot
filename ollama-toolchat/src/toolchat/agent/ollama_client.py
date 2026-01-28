import requests
from typing import List, Dict, Any, Optional
from ..config import settings
from ..infra.logging import get_logger

logger = get_logger(__name__)


class OllamaClient:
    def __init__(self, base_url: str = None, model: str = None):
        self.base_url = base_url or settings.ollama_url
        self.model = model or settings.ollama_model
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
        stream: bool = False,
    ) -> Dict[str, Any]:
        url = f"{self.base_url}/api/chat"
        
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": stream,
        }
        
        if tools:
            payload["tools"] = tools
        
        try:
            response = requests.post(url, json=payload, timeout=120)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Ollama API call failed: {e}", exc_info=True)
            raise
    
    def generate(self, prompt: str) -> str:
        url = f"{self.base_url}/api/generate"
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
        }
        
        try:
            response = requests.post(url, json=payload, timeout=120)
            response.raise_for_status()
            return response.json().get("response", "")
        except requests.exceptions.RequestException as e:
            logger.error(f"Ollama generate failed: {e}", exc_info=True)
            raise


ollama_client = OllamaClient()
