"""Process and performance monitoring command tool specifications."""

from .command_tool import CommandTool, CommandToolSpec
from ..base import ToolTier


def create_top_tool():
    """Top process viewer (batch mode)."""
    spec = CommandToolSpec(
        name="top_command",
        description="Show top processes by CPU/memory usage (batch mode, single iteration)",
        args_schema={"type": "object", "properties": {}},
        tier=ToolTier.READ_ONLY,
        requires_confirmation=False,
        supports_dry_run=False,
        allows_network=False,
        timeout_sec=10,
        binary="/usr/bin/top",
        argv_template=["-b", "-n", "1"]
    )
    return CommandTool(spec)


def create_htop_tool():
    """Htop process viewer (if available) - just checks availability."""
    spec = CommandToolSpec(
        name="htop_command",
        description="Check if htop is installed (htop is interactive and cannot show output directly)",
        args_schema={"type": "object", "properties": {}},
        tier=ToolTier.READ_ONLY,
        requires_confirmation=False,
        supports_dry_run=False,
        allows_network=False,
        timeout_sec=5,
        binary="/usr/bin/htop",
        argv_template=["--version"]
    )
    return CommandTool(spec)


def create_pidstat_tool():
    """Per-process statistics."""
    spec = CommandToolSpec(
        name="pidstat_command",
        description="Show per-process CPU, memory, and I/O statistics (from sysstat package)",
        args_schema={"type": "object", "properties": {}},
        tier=ToolTier.READ_ONLY,
        requires_confirmation=False,
        supports_dry_run=False,
        allows_network=False,
        timeout_sec=10,
        binary="/usr/bin/pidstat",
        argv_template=["1", "1"]
    )
    return CommandTool(spec)


def create_iotop_tool():
    """I/O monitoring by process."""
    spec = CommandToolSpec(
        name="iotop_command",
        description="Show I/O usage by process (batch mode, requires elevated permissions)",
        args_schema={"type": "object", "properties": {}},
        tier=ToolTier.READ_ONLY,
        requires_confirmation=False,
        supports_dry_run=False,
        allows_network=False,
        timeout_sec=10,
        binary="/usr/bin/iotop",
        argv_template=["-b", "-n", "1", "-o"]
    )
    return CommandTool(spec)
