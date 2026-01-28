import sqlite3
import json
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
from .logging import get_logger
from ..config import settings

logger = get_logger(__name__)


class AuditLogger:
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = Path(db_path) if db_path else Path(settings.audit_db_path)
        self._init_db()
    
    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                session_id TEXT,
                request_id TEXT,
                event_type TEXT NOT NULL,
                tool_name TEXT,
                tier INTEGER,
                action TEXT NOT NULL,
                details TEXT,
                result TEXT,
                user_confirmed BOOLEAN
            )
        """)
        
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON audit_log(timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_session ON audit_log(session_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tool ON audit_log(tool_name)")
        
        conn.commit()
        conn.close()
        logger.info(f"Initialized audit database at {self.db_path}")
    
    def log_tool_execution(
        self,
        session_id: str,
        request_id: str,
        tool_name: str,
        tier: int,
        action: str,
        details: Optional[Dict[str, Any]] = None,
        result: Optional[Dict[str, Any]] = None,
        user_confirmed: bool = False
    ) -> None:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            """
            INSERT INTO audit_log 
            (timestamp, session_id, request_id, event_type, tool_name, tier, action, details, result, user_confirmed)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                datetime.utcnow().isoformat(),
                session_id,
                request_id,
                "tool_execution",
                tool_name,
                tier,
                action,
                json.dumps(details) if details else None,
                json.dumps(result) if result else None,
                user_confirmed
            )
        )
        
        conn.commit()
        conn.close()
    
    def log_security_event(
        self,
        session_id: Optional[str],
        event_type: str,
        action: str,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            """
            INSERT INTO audit_log 
            (timestamp, session_id, event_type, action, details)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                datetime.utcnow().isoformat(),
                session_id,
                event_type,
                action,
                json.dumps(details) if details else None
            )
        )
        
        conn.commit()
        conn.close()
    
    def get_recent_logs(self, limit: int = 100) -> list:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            """
            SELECT timestamp, session_id, event_type, tool_name, tier, action, result, user_confirmed
            FROM audit_log
            ORDER BY timestamp DESC
            LIMIT ?
            """,
            (limit,)
        )
        
        logs = []
        for row in cursor.fetchall():
            logs.append({
                "timestamp": row[0],
                "session_id": row[1],
                "event_type": row[2],
                "tool_name": row[3],
                "tier": row[4],
                "action": row[5],
                "result": row[6],
                "user_confirmed": row[7]
            })
        
        conn.close()
        return logs


audit_logger = AuditLogger()
