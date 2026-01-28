"""File search and discovery command tool specifications."""

from .command_tool import CommandTool, CommandToolSpec
from ..base import ToolTier


def create_find_tool():
    """Find files and directories."""
    spec = CommandToolSpec(
        name="find_command",
        description="Search for files and directories. Use with path and options like -name, -type, -size, -mtime. Limited to READ_ROOTS.",
        args_schema={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Path to search in"},
                "name": {"type": "string", "description": "Name pattern to search for"}
            },
            "required": ["path"]
        },
        tier=ToolTier.READ_ONLY,
        requires_confirmation=False,
        supports_dry_run=False,
        allows_network=False,
        timeout_sec=30,
        binary="/usr/bin/find",
        argv_template=["{path}", "-maxdepth", "3", "-name", "{name}"]
    )
    return CommandTool(spec)


def create_fd_tool():
    """Modern file finder (fd-find)."""
    spec = CommandToolSpec(
        name="fd_command",
        description="Fast file finder (modern alternative to find). Search by name pattern.",
        args_schema={
            "type": "object",
            "properties": {
                "pattern": {"type": "string", "description": "Pattern to search for"},
                "path": {"type": "string", "description": "Path to search in"}
            },
            "required": ["pattern"]
        },
        tier=ToolTier.READ_ONLY,
        requires_confirmation=False,
        supports_dry_run=False,
        allows_network=False,
        timeout_sec=20,
        binary="/usr/bin/fdfind",
        argv_template=["-d", "3", "{pattern}", "{path}"]
    )
    return CommandTool(spec)


def create_rg_tool():
    """Ripgrep - fast text search."""
    spec = CommandToolSpec(
        name="rg_command",
        description="Search file contents using ripgrep (very fast grep alternative)",
        args_schema={
            "type": "object",
            "properties": {
                "pattern": {"type": "string", "description": "Text pattern to search for"},
                "path": {"type": "string", "description": "Path to search in"}
            },
            "required": ["pattern"]
        },
        tier=ToolTier.READ_ONLY,
        requires_confirmation=False,
        supports_dry_run=False,
        allows_network=False,
        timeout_sec=30,
        binary="/usr/bin/rg",
        argv_template=["-i", "--max-depth", "3", "{pattern}", "{path}"]
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
