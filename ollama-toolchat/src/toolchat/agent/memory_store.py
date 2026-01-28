from typing import Dict, List
from datetime import datetime
import uuid
from .persistence import persistence_store
from ..infra.logging import get_logger

logger = get_logger(__name__)


class MemoryStore:
    def __init__(self, use_persistence: bool = True):
        self.use_persistence = use_persistence
        self._sessions: Dict[str, List[Dict]] = {}
        
        if use_persistence:
            try:
                persistence_store._init_db()
                logger.info("Using SQLite persistence for chat history")
            except Exception as e:
                logger.warning(f"Failed to initialize persistence, using in-memory: {e}")
                self.use_persistence = False
    
    def create_session(self) -> str:
        session_id = str(uuid.uuid4())
        
        if self.use_persistence:
            try:
                persistence_store.create_session(session_id)
            except Exception as e:
                logger.error(f"Failed to create session in persistence: {e}")
                self._sessions[session_id] = []
        else:
            self._sessions[session_id] = []
        
        return session_id
    
    def add_message(self, session_id: str, role: str, content: str) -> None:
        if self.use_persistence:
            try:
                persistence_store.add_message(session_id, role, content)
                return
            except Exception as e:
                logger.error(f"Failed to add message to persistence: {e}")
        
        if session_id not in self._sessions:
            self._sessions[session_id] = []
        
        self._sessions[session_id].append({
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat(),
        })
    
    def get_history(self, session_id: str, limit: int = 50) -> List[Dict]:
        if self.use_persistence:
            try:
                return persistence_store.get_history(session_id, limit)
            except Exception as e:
                logger.error(f"Failed to get history from persistence: {e}")
        
        if session_id not in self._sessions:
            return []
        
        messages = self._sessions[session_id][-limit:]
        return [{"role": m["role"], "content": m["content"]} for m in messages]
    
    def clear_session(self, session_id: str) -> None:
        if self.use_persistence:
            try:
                persistence_store.clear_session(session_id)
                return
            except Exception as e:
                logger.error(f"Failed to clear session from persistence: {e}")
        
        if session_id in self._sessions:
            del self._sessions[session_id]
    
    def session_exists(self, session_id: str) -> bool:
        if self.use_persistence:
            try:
                return persistence_store.session_exists(session_id)
            except Exception as e:
                logger.error(f"Failed to check session in persistence: {e}")
        
        return session_id in self._sessions


memory_store = MemoryStore()
