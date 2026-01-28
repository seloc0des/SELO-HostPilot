import subprocess
from typing import Dict, Any
from .base import BaseTool, ToolSpec, ToolResult, ToolTier
from ..infra.logging import get_logger

logger = get_logger(__name__)


class GPUTemperatureTool(BaseTool):
    def __init__(self):
        spec = ToolSpec(
            name="gpu_temperature",
            description="Check GPU temperature and utilization using nvidia-smi. Shows temperature, utilization, memory usage, and power draw for NVIDIA GPUs.",
            args_schema={
                "type": "object",
                "properties": {},
                "required": []
            },
            tier=ToolTier.READ_ONLY,
            requires_confirmation=False,
            supports_dry_run=False,
        )
        super().__init__(spec)
    
    def execute(self, args: Dict[str, Any], dry_run: bool = False) -> ToolResult:
        try:
            # Check if nvidia-smi is available
            result = subprocess.run(
                ['nvidia-smi', '--query-gpu=index,name,temperature.gpu,utilization.gpu,memory.used,memory.total,power.draw', '--format=csv,noheader,nounits'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode != 0:
                return ToolResult(
                    ok=False,
                    error_code="nvidia_smi_error",
                    message="nvidia-smi command failed. Make sure NVIDIA drivers are installed and you have an NVIDIA GPU."
                )
            
            # Parse the output
            gpus = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    parts = [p.strip() for p in line.split(',')]
                    if len(parts) >= 7:
                        gpus.append({
                            "index": parts[0],
                            "name": parts[1],
                            "temperature_c": parts[2],
                            "utilization_percent": parts[3],
                            "memory_used_mb": parts[4],
                            "memory_total_mb": parts[5],
                            "power_draw_w": parts[6]
                        })
            
            if not gpus:
                return ToolResult(
                    ok=False,
                    error_code="no_gpu_found",
                    message="No NVIDIA GPUs found on this system."
                )
            
            return ToolResult(
                ok=True,
                data={
                    "gpu_count": len(gpus),
                    "gpus": gpus
                }
            )
            
        except FileNotFoundError:
            return ToolResult(
                ok=False,
                error_code="nvidia_smi_not_found",
                message="nvidia-smi not found. Install NVIDIA drivers to use this tool."
            )
        except subprocess.TimeoutExpired:
            return ToolResult(
                ok=False,
                error_code="timeout",
                message="nvidia-smi command timed out."
            )
        except Exception as e:
            logger.error(f"gpu_temperature failed: {e}", exc_info=True)
            return ToolResult(
                ok=False,
                error_code="gpu_temperature_error",
                message=f"Failed to check GPU temperature: {str(e)}"
            )
