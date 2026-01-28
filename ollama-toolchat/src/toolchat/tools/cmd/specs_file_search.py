"""File search and discovery command tool specifications."""

from .command_tool import CommandTool, CommandToolSpec
from ..base import ToolTier


def create_find_tool():
    """Find files and directories."""
    spec = CommandToolSpec(
        name="find_command",
        description="Search for files and directories. List all files in a path, or filter by name pattern.",
        args_schema={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Path/directory to search in (required)"},
                "name": {"type": "string", "description": "Name pattern to filter files (optional, defaults to '*' for all files)"}
            },
            "required": ["path"]
        },
        tier=ToolTier.READ_ONLY,
        requires_confirmation=False,
        supports_dry_run=False,
        allows_network=False,
        timeout_sec=30,
        binary="/usr/bin/find",
        argv_template=["{path}", "-maxdepth", "3", "-name", "{name}"],
        default_args={"name": "*"}
    )
    return CommandTool(spec)


def create_fd_tool():
    """Modern file finder (fd-find)."""
    spec = CommandToolSpec(
        name="fd_command",
        description="Fast file finder. List or search files in a directory. Use pattern to filter by name (optional, defaults to all files).",
        args_schema={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Path/directory to search in (required)"},
                "pattern": {"type": "string", "description": "Pattern to filter files by name (optional, defaults to '.' for all files)"}
            },
            "required": ["path"]
        },
        tier=ToolTier.READ_ONLY,
        requires_confirmation=False,
        supports_dry_run=False,
        allows_network=False,
        timeout_sec=20,
        binary="/usr/bin/fdfind",
        argv_template=["-d", "3", "{pattern}", "{path}"],
        default_args={"pattern": "."}
    )
    return CommandTool(spec)


def create_rg_tool():
    """Ripgrep - fast text search."""
    spec = CommandToolSpec(
        name="rg_command",
        description="Search file contents using ripgrep. Requires a text pattern to search for.",
        args_schema={
            "type": "object",
            "properties": {
                "pattern": {"type": "string", "description": "Text pattern to search for (required)"},
                "path": {"type": "string", "description": "Path to search in (optional, defaults to current directory)"}
            },
            "required": ["pattern"]
        },
        tier=ToolTier.READ_ONLY,
        requires_confirmation=False,
        supports_dry_run=False,
        allows_network=False,
        timeout_sec=30,
        binary="/usr/bin/rg",
        argv_template=["-i", "--max-depth", "3", "{pattern}", "{path}"],
        default_args={"path": "."}
    )
    return CommandTool(spec)


def create_tree_tool():
    """Directory tree visualization."""
    spec = CommandToolSpec(
        name="tree_command",
        description="Display directory structure as a tree. Use -L to limit depth.",
        args_schema={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Path to display"}
            },
            "required": ["path"]
        },
        tier=ToolTier.READ_ONLY,
        requires_confirmation=False,
        supports_dry_run=False,
        allows_network=False,
        timeout_sec=15,
        binary="/usr/bin/tree",
        argv_template=["-L", "2", "{path}"]
    )
    return CommandTool(spec)
