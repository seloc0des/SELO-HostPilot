from ..base import ToolTier
from .command_tool import CommandTool, CommandToolSpec


def create_journalctl_tool() -> CommandTool:
    spec = CommandToolSpec(
        name="journalctl_command",
        description="Query the systemd journal for system logs",
        args_schema={
            "type": "object",
            "properties": {
                "lines": {
                    "type": "integer",
                    "description": "Number of recent log lines to show (default: 50)",
                    "default": 50
                },
                "priority": {
                    "type": "string",
                    "description": "Filter by priority: emerg, alert, crit, err, warning, notice, info, debug",
                    "default": ""
                }
            }
        },
        tier=ToolTier.READ_ONLY,
        requires_confirmation=False,
        supports_dry_run=False,
        allows_network=False,
        timeout_sec=15,
        binary="/usr/bin/journalctl",
        argv_template=["-n", "{lines}", "--no-pager"]
    )
    return CommandTool(spec)


def create_dmesg_tool() -> CommandTool:
    spec = CommandToolSpec(
        name="dmesg_command",
        description="Print kernel ring buffer messages",
        args_schema={
            "type": "object",
            "properties": {
                "level": {
                    "type": "string",
                    "description": "Filter by log level: emerg, alert, crit, err, warn, notice, info, debug",
                    "default": ""
                }
            }
        },
        tier=ToolTier.READ_ONLY,
        requires_confirmation=False,
        supports_dry_run=False,
        allows_network=False,
        timeout_sec=10,
        binary="/usr/bin/dmesg",
        argv_template=["--human", "--nopager"]
    )
    return CommandTool(spec)
