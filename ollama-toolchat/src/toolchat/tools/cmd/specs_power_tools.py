"""Power user diagnostic tools - advanced but safe read-only operations."""

from .command_tool import CommandTool, CommandToolSpec
from ..base import ToolTier


def create_lsof_tool():
    """List open files."""
    spec = CommandToolSpec(
        name="lsof_command",
        description="List open files and network connections. Use -nP for numeric output, -i for internet connections.",
        args_schema={"type": "object", "properties": {}},
        tier=ToolTier.READ_ONLY,
        requires_confirmation=False,
        supports_dry_run=False,
        allows_network=False,
        timeout_sec=15,
        binary="/usr/bin/lsof",
        argv_template=["-nP"]
    )
    return CommandTool(spec)


def create_fuser_tool():
    """Identify processes using files/sockets."""
    spec = CommandToolSpec(
        name="fuser_command",
        description="Show which processes are using a file or socket",
        args_schema={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "File or socket path to check"}
            },
            "required": ["path"]
        },
        tier=ToolTier.READ_ONLY,
        requires_confirmation=False,
        supports_dry_run=False,
        allows_network=False,
        timeout_sec=10,
        binary="/usr/bin/fuser",
        argv_template=["-v", "{path}"]
    )
    return CommandTool(spec)


def create_file_tool():
    """Determine file type."""
    spec = CommandToolSpec(
        name="file_command",
        description="Determine file type and format",
        args_schema={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Path to file"}
            },
            "required": ["path"]
        },
        tier=ToolTier.READ_ONLY,
        requires_confirmation=False,
        supports_dry_run=False,
        allows_network=False,
        timeout_sec=5,
        binary="/usr/bin/file",
        argv_template=["-b", "{path}"]
    )
    return CommandTool(spec)


def create_ldd_tool():
    """Show shared library dependencies. WARNING: ldd can execute code from the target binary."""
    spec = CommandToolSpec(
        name="ldd_command",
        description="Display shared library dependencies of an executable (requires confirmation - security sensitive)",
        args_schema={
            "type": "object",
            "properties": {
                "binary": {"type": "string", "description": "Path to binary"}
            },
            "required": ["binary"]
        },
        tier=ToolTier.WRITE_SAFE,
        requires_confirmation=True,
        supports_dry_run=True,
        allows_network=False,
        timeout_sec=5,
        binary="/usr/bin/ldd",
        argv_template=["{binary}"]
    )
    return CommandTool(spec)


def create_last_tool():
    """Show last logged in users."""
    spec = CommandToolSpec(
        name="last_command",
        description="Show last logged in users (sensitive information)",
        args_schema={"type": "object", "properties": {}},
        tier=ToolTier.READ_ONLY,
        requires_confirmation=False,
        supports_dry_run=False,
        allows_network=False,
        timeout_sec=5,
        binary="/usr/bin/last",
        argv_template=["-n", "20"]
    )
    return CommandTool(spec)
