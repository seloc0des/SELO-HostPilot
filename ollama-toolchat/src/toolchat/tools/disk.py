import shutil
from typing import Dict, Any
from .base import BaseTool, ToolSpec, ToolResult, ToolTier
from ..infra.security import path_validator
from ..infra.logging import get_logger

logger = get_logger(__name__)


class DiskFreeTool(BaseTool):
    def __init__(self):
        spec = ToolSpec(
            name="disk_free",
            description="Check free disk space for a given path. Use '/home' for home directory or '/mnt/local' for mounted storage.",
            args_schema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to check disk space. Common paths: '/home', '/mnt/local', '/mnt/server'"
                    }
                },
                "required": ["path"]
            },
            tier=ToolTier.READ_ONLY,
            requires_confirmation=False,
            supports_dry_run=False,
        )
        super().__init__(spec)
    
    def execute(self, args: Dict[str, Any], dry_run: bool = False) -> ToolResult:
        path = args.get("path", "/home")
        
        try:
            validated_path = path_validator.validate_read(path)
            
            usage = shutil.disk_usage(validated_path)
            
            total_gb = usage.total / (1024**3)
            used_gb = usage.used / (1024**3)
            free_gb = usage.free / (1024**3)
            percent_used = (usage.used / usage.total) * 100
            
            return ToolResult(
                ok=True,
                data={
                    "path": str(validated_path),
                    "total_gb": round(total_gb, 2),
                    "used_gb": round(used_gb, 2),
                    "free_gb": round(free_gb, 2),
                    "percent_used": round(percent_used, 1),
                }
            )
        except Exception as e:
            logger.error(f"disk_free failed for {path}", exc_info=True)
            return ToolResult(
                ok=False,
                error_code="disk_free_error",
                message=f"Failed to check disk space: {str(e)}"
            )
