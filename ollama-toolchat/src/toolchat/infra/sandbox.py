import subprocess
from typing import List, Optional, Dict, Any
from ..config import settings
from .logging import get_logger

logger = get_logger(__name__)


class SandboxError(Exception):
    pass


class SandboxRunner:
    def __init__(self, mode: str = "none"):
        self.mode = mode
    
    def run(
        self,
        command: List[str],
        cwd: Optional[str] = None,
        timeout: int = 30,
        env: Optional[Dict[str, str]] = None,
        allow_network: bool = False,
        read_paths: Optional[List[str]] = None,
        write_paths: Optional[List[str]] = None,
        max_output_bytes: int = 10000,
    ) -> Dict[str, Any]:
        if self.mode == "systemd":
            return self._run_systemd(command, cwd, timeout, env, allow_network, read_paths, write_paths, max_output_bytes)
        elif self.mode == "bwrap":
            return self._run_bwrap(command, cwd, timeout, env, allow_network, read_paths, write_paths, max_output_bytes)
        else:
            return self._run_direct(command, cwd, timeout, env, max_output_bytes)
    
    def _run_direct(
        self,
        command: List[str],
        cwd: Optional[str],
        timeout: int,
        env: Optional[Dict[str, str]],
        max_output_bytes: int = 10000,
    ) -> Dict[str, Any]:
        try:
            result = subprocess.run(
                command,
                cwd=cwd,
                timeout=timeout,
                capture_output=True,
                text=True,
                env=env,
            )
            
            return {
                "ok": result.returncode == 0,
                "exit_code": result.returncode,
                "stdout": result.stdout[:max_output_bytes],
                "stderr": result.stderr[:max_output_bytes],
            }
        except subprocess.TimeoutExpired:
            logger.error(f"Command timed out: {command}")
            return {
                "ok": False,
                "exit_code": -1,
                "stdout": "",
                "stderr": f"Command timed out after {timeout}s",
            }
        except Exception as e:
            logger.error(f"Command failed: {command}", exc_info=True)
            return {
                "ok": False,
                "exit_code": -1,
                "stdout": "",
                "stderr": str(e),
            }
    
    def _run_systemd(
        self,
        command: List[str],
        cwd: Optional[str],
        timeout: int,
        env: Optional[Dict[str, str]],
        allow_network: bool,
        read_paths: Optional[List[str]],
        write_paths: Optional[List[str]],
        max_output_bytes: int = 10000,
    ) -> Dict[str, Any]:
        systemd_cmd = [
            "systemd-run",
            "--user",
            "--scope",
            "--quiet",
            "--collect",
            f"--property=MemoryMax=512M",
            f"--property=CPUQuota=50%",
            f"--property=TimeoutStopSec={timeout}",
            "--property=ProtectSystem=strict",
            "--property=ProtectHome=read-only",
            "--property=PrivateTmp=yes",
            "--property=NoNewPrivileges=yes",
        ]
        
        if not allow_network:
            systemd_cmd.append("--property=RestrictAddressFamilies=")
        
        if write_paths:
            for wp in write_paths:
                systemd_cmd.append(f"--property=ReadWritePaths={wp}")
        
        systemd_cmd.extend(command)
        
        return self._run_direct(systemd_cmd, cwd, timeout, env, max_output_bytes)
    
    def _run_bwrap(
        self,
        command: List[str],
        cwd: Optional[str],
        timeout: int,
        env: Optional[Dict[str, str]],
        allow_network: bool,
        read_paths: Optional[List[str]],
        write_paths: Optional[List[str]],
        max_output_bytes: int = 10000,
    ) -> Dict[str, Any]:
        bwrap_cmd = [
            "bwrap",
            "--ro-bind", "/usr", "/usr",
            "--ro-bind", "/lib", "/lib",
            "--ro-bind", "/lib64", "/lib64",
            "--ro-bind", "/bin", "/bin",
            "--ro-bind", "/sbin", "/sbin",
            "--tmpfs", "/tmp",
            "--proc", "/proc",
            "--dev", "/dev",
            "--unshare-all",
        ]
        
        if allow_network:
            bwrap_cmd.append("--share-net")
        
        if read_paths:
            for rp in read_paths:
                bwrap_cmd.extend(["--ro-bind", rp, rp])
        
        if write_paths:
            for wp in write_paths:
                bwrap_cmd.extend(["--bind", wp, wp])
        
        if cwd:
            bwrap_cmd.extend(["--chdir", cwd])
        
        bwrap_cmd.append("--")
        bwrap_cmd.extend(command)
        
        return self._run_direct(bwrap_cmd, None, timeout, env, max_output_bytes)


sandbox_runner = SandboxRunner(mode=settings.sandbox_mode)
