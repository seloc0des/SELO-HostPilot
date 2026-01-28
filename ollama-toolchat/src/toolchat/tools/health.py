import psutil
from typing import Dict, Any
from .base import BaseTool, ToolSpec, ToolResult, ToolTier
from ..infra.logging import get_logger

logger = get_logger(__name__)


class SystemHealthTool(BaseTool):
    def __init__(self):
        spec = ToolSpec(
            name="system_health",
            description="Check system health including CPU, memory, and top processes",
            args_schema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Number of top processes to return (default: 5)",
                        "default": 5
                    }
                }
            },
            tier=ToolTier.READ_ONLY,
            requires_confirmation=False,
            supports_dry_run=False,
        )
        super().__init__(spec)
    
    def execute(self, args: Dict[str, Any], dry_run: bool = False) -> ToolResult:
        limit = args.get("limit", 5)
        
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_used_gb = memory.used / (1024**3)
            memory_total_gb = memory.total / (1024**3)
            
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    pinfo = proc.info
                    processes.append({
                        'pid': pinfo['pid'],
                        'name': pinfo['name'],
                        'cpu_percent': pinfo['cpu_percent'] or 0,
                        'memory_percent': pinfo['memory_percent'] or 0,
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            top_cpu = sorted(processes, key=lambda x: x['cpu_percent'], reverse=True)[:limit]
            top_memory = sorted(processes, key=lambda x: x['memory_percent'], reverse=True)[:limit]
            
            return ToolResult(
                ok=True,
                data={
                    "cpu_percent": round(cpu_percent, 1),
                    "memory_percent": round(memory_percent, 1),
                    "memory_used_gb": round(memory_used_gb, 2),
                    "memory_total_gb": round(memory_total_gb, 2),
                    "top_cpu_processes": top_cpu,
                    "top_memory_processes": top_memory,
                }
            )
        except Exception as e:
            logger.error("system_health failed", exc_info=True)
            return ToolResult(
                ok=False,
                error_code="system_health_error",
                message=f"Failed to check system health: {str(e)}"
            )
