import pytest
import tempfile
import os
from pathlib import Path
from src.toolchat.agent.persistence import PersistenceStore


@pytest.fixture
def temp_db():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    
    yield db_path
    
    if os.path.exists(db_path):
        os.unlink(db_path)


def test_persistence_store_init(temp_db):
    store = PersistenceStore(db_path=temp_db)
    assert Path(temp_db).exists()


def test_create_session(temp_db):
    store = PersistenceStore(db_path=temp_db)
    session_id = "test-session-123"
    
    store.create_session(session_id)
    assert store.session_exists(session_id)


def test_add_and_get_messages(temp_db):
    store = PersistenceStore(db_path=temp_db)
    session_id = "test-session-456"
    
    store.create_session(session_id)
    store.add_message(session_id, "user", "Hello")
    store.add_message(session_id, "assistant", "Hi there")
    
    history = store.get_history(session_id)
    
    assert len(history) == 2
    assert history[0]["role"] == "user"
    assert history[0]["content"] == "Hello"
    assert history[1]["role"] == "assistant"
    assert history[1]["content"] == "Hi there"


def test_clear_session(temp_db):
    store = PersistenceStore(db_path=temp_db)
    session_id = "test-session-789"
    
    store.create_session(session_id)
    store.add_message(session_id, "user", "Test")
    
    assert store.session_exists(session_id)
    
    store.clear_session(session_id)
    
    assert not store.session_exists(session_id)


def test_get_all_sessions(temp_db):
    store = PersistenceStore(db_path=temp_db)
    
    store.create_session("session-1")
    store.create_session("session-2")
    store.add_message("session-1", "user", "Message 1")
    store.add_message("session-2", "user", "Message 2")
    
    sessions = store.get_all_sessions()
    
    assert len(sessions) >= 2
    session_ids = [s["session_id"] for s in sessions]
    assert "session-1" in session_ids
    assert "session-2" in session_ids
