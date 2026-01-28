from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
from pathlib import Path
import os

# Find project root (2 levels up from this file: src/toolchat/config.py)
PROJECT_ROOT = Path(__file__).parent.parent.parent
ENV_FILE = PROJECT_ROOT / ".env"

# Get user home directory dynamically
_HOME = str(Path.home())

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=str(ENV_FILE), env_file_encoding="utf-8", extra="ignore")
    
    toolchat_host: str = "127.0.0.1"
    toolchat_port: int = 8000
    ollama_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1"
    read_roots: str = f"{_HOME},/mnt/local,/mnt/server"
    write_roots: str = f"{_HOME}/Pictures/Inbox,{_HOME}/Pictures/Organized"
    sandbox_mode: str = "none"
    allow_network: bool = False
    log_level: str = "INFO"
    audit_db_path: str = "ollama-toolchat-audit.db"
    chat_db_path: str = "ollama-toolchat-chat.db"
    
    @property
    def read_roots_list(self) -> List[str]:
        return [r.strip() for r in self.read_roots.split(",") if r.strip()]
    
    @property
    def write_roots_list(self) -> List[str]:
        return [r.strip() for r in self.write_roots.split(",") if r.strip()]


settings = Settings()
