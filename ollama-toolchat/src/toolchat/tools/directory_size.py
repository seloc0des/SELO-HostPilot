import subprocess
from typing import Dict, Any
from .base import BaseTool, ToolSpec, ToolResult, ToolTier
from ..infra.security import path_validator
from ..infra.logging import get_logger

logger = get_logger(__name__)


class DirectorySizeTool(BaseTool):
    def __init__(self):
        spec = ToolSpec(
            name="directory_size",
            description="Analyze directory sizes to find which directories are taking up the most space. Shows top directories sorted by size. Use path like '/home/sean' or '/mnt/local'.",
            args_schema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to analyze. Common paths: '/home/sean', '/mnt/local', '/mnt/server'"
                    },
                    "depth": {
                        "type": "integer",
                        "description": "Maximum depth to analyze (1-3). Default is 1 for immediate subdirectories.",
                        "default": 1
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
        depth = args.get("depth", 1)
        
        # Validate depth
        if depth < 1 or depth > 3:
            return ToolResult(
                ok=False,
                error_code="invalid_depth",
                message="Depth must be between 1 and 3"
            )
        
        try:
            # Validate path access
            validated_path = path_validator.validate_read(path)
            
            # Use du to get directory sizes
            result = subprocess.run(
                ['du', '-h', f'--max-depth={depth}', str(validated_path)],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                return ToolResult(
                    ok=False,
                    error_code="du_command_error",
                    message=f"Failed to analyze directory: {result.stderr}"
                )
            
            # Parse and sort the output
            lines = result.stdout.strip().split('\n')
            directories = []
            
            for line in lines:
                if line:
                    parts = line.split('\t', 1)
                    if len(parts) == 2:
                        size, dir_path = parts
                        directories.append({
                            "size": size,
                            "path": dir_path
                        })
            
            # Sort by size (convert to bytes for proper sorting)
            def size_to_bytes(size_str):
                """Convert human-readable size to bytes for sorting"""
                size_str = size_str.strip()
                multipliers = {'K': 1024, 'M': 1024**2, 'G': 1024**3, 'T': 1024**4}
                
                if size_str[-1] in multipliers:
                    return float(size_str[:-1]) * multipliers[size_str[-1]]
                return float(size_str)
            
            directories.sort(key=lambda x: size_to_bytes(x['size']), reverse=True)
            
            # Take top 20
            top_directories = directories[:20]
            
            return ToolResult(
                ok=True,
                data={
                    "analyzed_path": str(validated_path),
                    "depth": depth,
                    "total_directories": len(directories),
                    "top_directories": top_directories
                }
            )
            
        except subprocess.TimeoutExpired:
            return ToolResult(
                ok=False,
                error_code="timeout",
                message="Directory analysis timed out. Try a smaller depth or more specific path."
            )
        except Exception as e:
            logger.error(f"directory_size failed for {path}", exc_info=True)
            return ToolResult(
                ok=False,
                error_code="directory_size_error",
                message=f"Failed to analyze directory sizes: {str(e)}"
            )
