"""Security and access control command tool specifications."""

from .command_tool import CommandTool, CommandToolSpec
from ..base import ToolTier


def create_ufw_status_tool():
    """UFW firewall status."""
    spec = CommandToolSpec(
        name="ufw_status_command",
        description="Show UFW (Uncomplicated Firewall) status and rules",
        args_schema={"type": "object", "properties": {}},
        tier=ToolTier.READ_ONLY,
        requires_confirmation=False,
        supports_dry_run=False,
        allows_network=False,
        timeout_sec=5,
        binary="/usr/sbin/ufw",
        argv_template=["status", "verbose"]
    )
    return CommandTool(spec)


def create_aa_status_tool():
    """AppArmor status."""
    spec = CommandToolSpec(
        name="aa_status_command",
        description="Show AppArmor security profiles status",
        args_schema={"type": "object", "properties": {}},
        tier=ToolTier.READ_ONLY,
        requires_confirmation=False,
        supports_dry_run=False,
        allows_network=False,
        timeout_sec=5,
        binary="/usr/sbin/aa-status",
        argv_template=[]
    )
    return CommandTool(spec)


def create_loginctl_tool():
    """Login session management."""
    spec = CommandToolSpec(
        name="loginctl_command",
        description="Show user login sessions and seat information",
        args_schema={"type": "object", "properties": {}},
        tier=ToolTier.READ_ONLY,
        requires_confirmation=False,
        supports_dry_run=False,
        allows_network=False,
        timeout_sec=5,
        binary="/usr/bin/loginctl",
        argv_template=["list-sessions"]
    )
    return CommandTool(spec)
