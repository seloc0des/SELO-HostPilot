import sqlite3
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
from ..infra.logging import get_logger
from ..config import settings

logger = get_logger(__name__)


class PersistenceStore:
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = Path(db_path) if db_path else Path(settings.chat_db_path)
        self._init_db()
    
    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                created_at TEXT NOT NULL,
                last_active TEXT NOT NULL
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (session_id) REFERENCES sessions(session_id)
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_messages_session 
            ON messages(session_id, timestamp)
        """)
        
        conn.commit()
        conn.close()
        logger.info(f"Initialized persistence database at {self.db_path}")
    
    def create_session(self, session_id: str) -> None:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        now = datetime.utcnow().isoformat()
        cursor.execute(
            "INSERT OR IGNORE INTO sessions (session_id, created_at, last_active) VALUES (?, ?, ?)",
            (session_id, now, now)
        )
        
        conn.commit()
        conn.close()
    
    def session_exists(self, session_id: str) -> bool:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT 1 FROM sessions WHERE session_id = ?", (session_id,))
        exists = cursor.fetchone() is not None
        
        conn.close()
        return exists
    
    def add_message(self, session_id: str, role: str, content: str) -> None:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        now = datetime.utcnow().isoformat()
        
        cursor.execute(
            "UPDATE sessions SET last_active = ? WHERE session_id = ?",
            (now, session_id)
        )
        
        cursor.execute(
            "INSERT INTO messages (session_id, role, content, timestamp) VALUES (?, ?, ?, ?)",
            (session_id, role, content, now)
        )
        
        conn.commit()
        conn.close()
    
    def get_history(self, session_id: str, limit: int = 50) -> List[Dict]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            """
            SELECT role, content, timestamp 
            FROM messages 
            WHERE session_id = ? 
            ORDER BY timestamp DESC 
            LIMIT ?
            """,
            (session_id, limit)
        )
        
        messages = []
        for row in cursor.fetchall():
            messages.append({
                "role": row[0],
                "content": row[1],
                "timestamp": row[2]
            })
        
        conn.close()
        
        messages.reverse()
        return [{"role": m["role"], "content": m["content"]} for m in messages]
    
    def clear_session(self, session_id: str) -> None:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
        cursor.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
        
        conn.commit()
        conn.close()
    
    def get_all_sessions(self) -> List[Dict]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            """
            SELECT s.session_id, s.created_at, s.last_active, COUNT(m.id) as message_count
            FROM sessions s
            LEFT JOIN messages m ON s.session_id = m.session_id
            GROUP BY s.session_id
            ORDER BY s.last_active DESC
            """
        )
        
        sessions = []
        for row in cursor.fetchall():
            sessions.append({
                "session_id": row[0],
                "created_at": row[1],
                "last_active": row[2],
                "message_count": row[3]
            })
        
        conn.close()
        return sessions


persistence_store = PersistenceStore()
