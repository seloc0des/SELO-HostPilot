from ..base import ToolTier
from .command_tool import CommandTool, CommandToolSpec


def create_df_tool() -> CommandTool:
    spec = CommandToolSpec(
        name="df_command",
        description="Show disk filesystem usage with human-readable sizes",
        args_schema={
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to check (optional, defaults to all filesystems)",
                    "default": ""
                }
            }
        },
        tier=ToolTier.READ_ONLY,
        requires_confirmation=False,
        supports_dry_run=False,
        allows_network=False,
        timeout_sec=10,
        binary="/usr/bin/df",
        argv_template=["-h", "{path}"]
    )
    return CommandTool(spec)


def create_du_tool() -> CommandTool:
    spec = CommandToolSpec(
        name="du_command",
        description="Estimate disk usage of a directory",
        args_schema={
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Directory path to analyze",
                    "default": "."
                },
                "max_depth": {
                    "type": "integer",
                    "description": "Maximum depth to display (default: 1)",
                    "default": 1
                }
            }
        },
        tier=ToolTier.READ_ONLY,
        requires_confirmation=False,
        supports_dry_run=False,
        allows_network=False,
        timeout_sec=30,
        binary="/usr/bin/du",
        argv_template=["-h", "--max-depth={max_depth}", "{path}"]
    )
    return CommandTool(spec)


def create_lsblk_tool() -> CommandTool:
    spec = CommandToolSpec(
        name="lsblk_command",
        description="List block devices and their mount points",
        args_schema={
            "type": "object",
            "properties": {}
        },
        tier=ToolTier.READ_ONLY,
        requires_confirmation=False,
        supports_dry_run=False,
        allows_network=False,
        timeout_sec=10,
        binary="/usr/bin/lsblk",
        argv_template=["-f"]
    )
    return CommandTool(spec)


def create_findmnt_tool() -> CommandTool:
    spec = CommandToolSpec(
        name="findmnt_command",
        description="Find and display mounted filesystems",
        args_schema={
            "type": "object",
            "properties": {
                "target": {
                    "type": "string",
                    "description": "Mount point or device to find (optional)",
                    "default": ""
                }
            }
        },
        tier=ToolTier.READ_ONLY,
        requires_confirmation=False,
        supports_dry_run=False,
        allows_network=False,
        timeout_sec=10,
        binary="/usr/bin/findmnt",
        argv_template=["{target}"]
    )
    return CommandTool(spec)
