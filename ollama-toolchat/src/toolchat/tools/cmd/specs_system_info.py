"""System information and environment command tool specifications."""

from .command_tool import CommandTool, CommandToolSpec
from ..base import ToolTier


def create_uname_tool():
    """System information via uname."""
    spec = CommandToolSpec(
        name="uname_command",
        description="Show system information (kernel, architecture, OS). Use -a for all info.",
        args_schema={"type": "object", "properties": {}},
        tier=ToolTier.READ_ONLY,
        requires_confirmation=False,
        supports_dry_run=False,
        allows_network=False,
        timeout_sec=5,
        binary="/usr/bin/uname",
        argv_template=["-a"]
    )
    return CommandTool(spec)


def create_hostname_tool():
    """Show system hostname."""
    spec = CommandToolSpec(
        name="hostname_command",
        description="Display the system's hostname",
        args_schema={"type": "object", "properties": {}},
        tier=ToolTier.READ_ONLY,
        requires_confirmation=False,
        supports_dry_run=False,
        allows_network=False,
        timeout_sec=5,
        binary="/usr/bin/hostname",
        argv_template=[]
    )
    return CommandTool(spec)


def create_whoami_tool():
    """Show current user."""
    spec = CommandToolSpec(
        name="whoami_command",
        description="Display the current username",
        args_schema={"type": "object", "properties": {}},
        tier=ToolTier.READ_ONLY,
        requires_confirmation=False,
        supports_dry_run=False,
        allows_network=False,
        timeout_sec=5,
        binary="/usr/bin/whoami",
        argv_template=[]
    )
    return CommandTool(spec)


def create_id_tool():
    """Show user and group IDs."""
    spec = CommandToolSpec(
        name="id_command",
        description="Display user and group IDs for the current user",
        args_schema={"type": "object", "properties": {}},
        tier=ToolTier.READ_ONLY,
        requires_confirmation=False,
        supports_dry_run=False,
        allows_network=False,
        timeout_sec=5,
        binary="/usr/bin/id",
        argv_template=[]
    )
    return CommandTool(spec)


def create_env_tool():
    """Show environment variables."""
    spec = CommandToolSpec(
        name="env_command",
        description="Display all environment variables",
        args_schema={"type": "object", "properties": {}},
        tier=ToolTier.READ_ONLY,
        requires_confirmation=False,
        supports_dry_run=False,
        allows_network=False,
        timeout_sec=5,
        binary="/usr/bin/env",
        argv_template=[]
    )
    return CommandTool(spec)


def create_timedatectl_tool():
    """Show system time and date settings."""
    spec = CommandToolSpec(
        name="timedatectl_command",
        description="Display system time, date, and timezone information",
        args_schema={"type": "object", "properties": {}},
        tier=ToolTier.READ_ONLY,
        requires_confirmation=False,
        supports_dry_run=False,
        allows_network=False,
        timeout_sec=5,
        binary="/usr/bin/timedatectl",
        argv_template=["status"]
    )
    return CommandTool(spec)


def create_locale_tool():
    """Show locale settings."""
    spec = CommandToolSpec(
        name="locale_command",
        description="Display locale and language settings",
        args_schema={"type": "object", "properties": {}},
        tier=ToolTier.READ_ONLY,
        requires_confirmation=False,
        supports_dry_run=False,
        allows_network=False,
        timeout_sec=5,
        binary="/usr/bin/locale",
        argv_template=[]
    )
    return CommandTool(spec)
