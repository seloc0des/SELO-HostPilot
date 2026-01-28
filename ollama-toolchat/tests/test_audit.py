import pytest
import tempfile
import os
from pathlib import Path
from src.toolchat.infra.audit import AuditLogger


@pytest.fixture
def temp_audit_db():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    
    yield db_path
    
    if os.path.exists(db_path):
        os.unlink(db_path)


def test_audit_logger_init(temp_audit_db):
    logger = AuditLogger(db_path=temp_audit_db)
    assert Path(temp_audit_db).exists()


def test_log_tool_execution(temp_audit_db):
    logger = AuditLogger(db_path=temp_audit_db)
    
    logger.log_tool_execution(
        session_id="test-session",
        request_id="test-request",
        tool_name="disk_free",
        tier=0,
        action="execute",
        details={"path": "/"},
        result={"ok": True},
        user_confirmed=False
    )
    
    logs = logger.get_recent_logs(limit=10)
    
    assert len(logs) > 0
    assert logs[0]["tool_name"] == "disk_free"
    assert logs[0]["tier"] == 0
    assert logs[0]["action"] == "execute"


def test_log_security_event(temp_audit_db):
    logger = AuditLogger(db_path=temp_audit_db)
    
    logger.log_security_event(
        session_id="test-session",
        event_type="path_denied",
        action="read_attempt",
        details={"path": "/etc/shadow"}
    )
    
    logs = logger.get_recent_logs(limit=10)
    
    assert len(logs) > 0
    assert logs[0]["event_type"] == "path_denied"
    assert logs[0]["action"] == "read_attempt"


def test_get_recent_logs_limit(temp_audit_db):
    logger = AuditLogger(db_path=temp_audit_db)
    
    for i in range(20):
        logger.log_tool_execution(
            session_id=f"session-{i}",
            request_id=f"request-{i}",
            tool_name="test_tool",
            tier=0,
            action="execute",
            user_confirmed=False
        )
    
    logs = logger.get_recent_logs(limit=5)
    
    assert len(logs) == 5
