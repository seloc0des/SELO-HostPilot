from typing import List, Optional, Dict, Any
from ...infra.sandbox import sandbox_runner
from ...infra.security import path_validator
from ...infra.logging import get_logger

logger = get_logger(__name__)


class CommandRunner:
    def run_command(
        self,
        command: List[str],
        cwd: Optional[str] = None,
        timeout: int = 30,
        allow_network: bool = False,
        read_paths: Optional[List[str]] = None,
        write_paths: Optional[List[str]] = None,
        max_output_bytes: int = 10000,
    ) -> Dict[str, Any]:
        if cwd and not path_validator.can_read(cwd):
            return {
                "ok": False,
                "exit_code": -1,
                "stdout": "",
                "stderr": f"Access denied to directory: {cwd}",
            }
        
        if read_paths:
            for rp in read_paths:
                if not path_validator.can_read(rp):
                    return {
                        "ok": False,
                        "exit_code": -1,
                        "stdout": "",
                        "stderr": f"Read access denied: {rp}",
                    }
        
        if write_paths:
            for wp in write_paths:
                if not path_validator.can_write(wp):
                    return {
                        "ok": False,
                        "exit_code": -1,
                        "stdout": "",
                        "stderr": f"Write access denied: {wp}",
                    }
        
        logger.info(f"Running command: {' '.join(command)}", extra={
            "tool_name": "cmd_runner",
            "cwd": cwd,
        })
        
        result = sandbox_runner.run(
            command=command,
            cwd=cwd,
            timeout=timeout,
            allow_network=allow_network,
            read_paths=read_paths,
            write_paths=write_paths,
            max_output_bytes=max_output_bytes,
        )
        
        return result


command_runner = CommandRunner()
