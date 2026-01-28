from ..base import ToolTier
from .command_tool import CommandTool, CommandToolSpec


def create_ps_tool() -> CommandTool:
    spec = CommandToolSpec(
        name="ps_command",
        description="Display information about running processes (shows all users)",
        args_schema={
            "type": "object",
            "properties": {}
        },
        tier=ToolTier.READ_ONLY,
        requires_confirmation=False,
        supports_dry_run=False,
        allows_network=False,
        timeout_sec=10,
        binary="/usr/bin/ps",
        argv_template=["aux"]
    )
    return CommandTool(spec)


def create_free_tool() -> CommandTool:
    spec = CommandToolSpec(
        name="free_command",
        description="Display amount of free and used memory",
        args_schema={
            "type": "object",
            "properties": {}
        },
        tier=ToolTier.READ_ONLY,
        requires_confirmation=False,
        supports_dry_run=False,
        allows_network=False,
        timeout_sec=5,
        binary="/usr/bin/free",
        argv_template=["-h"]
    )
    return CommandTool(spec)


def create_vmstat_tool() -> CommandTool:
    spec = CommandToolSpec(
        name="vmstat_command",
        description="Report virtual memory statistics",
        args_schema={
            "type": "object",
            "properties": {}
        },
        tier=ToolTier.READ_ONLY,
        requires_confirmation=False,
        supports_dry_run=False,
        allows_network=False,
        timeout_sec=5,
        binary="/usr/bin/vmstat",
        argv_template=[]
    )
    return CommandTool(spec)


def create_iostat_tool() -> CommandTool:
    spec = CommandToolSpec(
        name="iostat_command",
        description="Report CPU and I/O statistics",
        args_schema={
            "type": "object",
            "properties": {}
        },
        tier=ToolTier.READ_ONLY,
        requires_confirmation=False,
        supports_dry_run=False,
        allows_network=False,
        timeout_sec=10,
        binary="/usr/bin/iostat",
        argv_template=["-x"]
    )
    return CommandTool(spec)


def create_uptime_tool() -> CommandTool:
    spec = CommandToolSpec(
        name="uptime_command",
        description="Show how long the system has been running",
        args_schema={
            "type": "object",
            "properties": {}
        },
        tier=ToolTier.READ_ONLY,
        requires_confirmation=False,
        supports_dry_run=False,
        allows_network=False,
        timeout_sec=5,
        binary="/usr/bin/uptime",
        argv_template=[]
    )
    return CommandTool(spec)
