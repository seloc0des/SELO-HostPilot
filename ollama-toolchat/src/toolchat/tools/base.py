from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field
from enum import IntEnum


class ToolTier(IntEnum):
    READ_ONLY = 0
    WRITE_SAFE = 1
    SYSTEM_CHANGE = 2


class ToolResult(BaseModel):
    ok: bool
    data: Optional[Any] = None
    error_code: Optional[str] = None
    message: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


class ToolSpec(BaseModel):
    name: str
    description: str
    args_schema: Dict[str, Any]
    tier: ToolTier = ToolTier.READ_ONLY
    requires_confirmation: bool = False
    supports_dry_run: bool = False
    allows_network: bool = False
    timeout_sec: int = 30
    max_output_bytes: int = 10000


class BaseTool(ABC):
    def __init__(self, spec: ToolSpec):
        self.spec = spec
    
    @abstractmethod
    def execute(self, args: Dict[str, Any], dry_run: bool = False) -> ToolResult:
        pass
    
    def validate_args(self, args: Dict[str, Any]) -> bool:
        return True
