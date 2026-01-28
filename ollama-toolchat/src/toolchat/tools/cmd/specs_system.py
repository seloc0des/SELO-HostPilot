from ..base import ToolTier
from .command_tool import CommandTool, CommandToolSpec


def create_apt_install_tool() -> CommandTool:
    """
    Install packages using apt. Requires sudo privileges.
    This is a Tier 2 tool that requires explicit user confirmation.
    """
    spec = CommandToolSpec(
        name="apt_install",
        description="Install a package using apt package manager (requires sudo and confirmation)",
        args_schema={
            "type": "object",
            "properties": {
                "package": {
                    "type": "string",
                    "description": "Package name to install"
                },
                "dry_run": {
                    "type": "boolean",
                    "description": "If true, simulate the installation",
                    "default": True
                }
            },
            "required": ["package"]
        },
        tier=ToolTier.SYSTEM_CHANGE,
        requires_confirmation=True,
        supports_dry_run=True,
        allows_network=True,
        timeout_sec=300,
        binary="/usr/bin/sudo",
        argv_template=["apt-get", "install", "-y", "{package}"]
    )
    return CommandTool(spec)


def create_apt_update_tool() -> CommandTool:
    """
    Update apt package lists. Requires sudo privileges.
    This is a Tier 2 tool that requires explicit user confirmation.
    """
    spec = CommandToolSpec(
        name="apt_update",
        description="Update apt package lists (requires sudo and confirmation)",
        args_schema={
            "type": "object",
            "properties": {}
        },
        tier=ToolTier.SYSTEM_CHANGE,
        requires_confirmation=True,
        supports_dry_run=False,
        allows_network=True,
        timeout_sec=120,
        binary="/usr/bin/sudo",
        argv_template=["apt-get", "update"]
    )
    return CommandTool(spec)


def create_systemctl_status_tool() -> CommandTool:
    """
    Check status of a systemd service. Read-only operation.
    """
    spec = CommandToolSpec(
        name="systemctl_status",
        description="Check the status of a systemd service",
        args_schema={
            "type": "object",
            "properties": {
                "service": {
                    "type": "string",
                    "description": "Service name to check"
                }
            },
            "required": ["service"]
        },
        tier=ToolTier.READ_ONLY,
        requires_confirmation=False,
        supports_dry_run=False,
        allows_network=False,
        timeout_sec=10,
        binary="/usr/bin/systemctl",
        argv_template=["status", "{service}"]
    )
    return CommandTool(spec)


def create_systemctl_restart_tool() -> CommandTool:
    """
    Restart a systemd service. Requires sudo privileges.
    This is a Tier 2 tool that requires explicit user confirmation.
    """
    spec = CommandToolSpec(
        name="systemctl_restart",
        description="Restart a systemd service (requires sudo and confirmation)",
        args_schema={
            "type": "object",
            "properties": {
                "service": {
                    "type": "string",
                    "description": "Service name to restart"
                }
            },
            "required": ["service"]
        },
        tier=ToolTier.SYSTEM_CHANGE,
        requires_confirmation=True,
        supports_dry_run=False,
        allows_network=False,
        timeout_sec=60,
        binary="/usr/bin/sudo",
        argv_template=["systemctl", "restart", "{service}"]
    )
    return CommandTool(spec)


def create_systemctl_start_tool() -> CommandTool:
    """
    Start a systemd service. Requires sudo privileges.
    This is a Tier 2 tool that requires explicit user confirmation.
    """
    spec = CommandToolSpec(
        name="systemctl_start",
        description="Start a systemd service (requires sudo and confirmation)",
        args_schema={
            "type": "object",
            "properties": {
                "service": {
                    "type": "string",
                    "description": "Service name to start"
                }
            },
            "required": ["service"]
        },
        tier=ToolTier.SYSTEM_CHANGE,
        requires_confirmation=True,
        supports_dry_run=False,
        allows_network=False,
        timeout_sec=60,
        binary="/usr/bin/sudo",
        argv_template=["systemctl", "start", "{service}"]
    )
    return CommandTool(spec)


def create_systemctl_stop_tool() -> CommandTool:
    """
    Stop a systemd service. Requires sudo privileges.
    This is a Tier 2 tool that requires explicit user confirmation.
    """
    spec = CommandToolSpec(
        name="systemctl_stop",
        description="Stop a systemd service (requires sudo and confirmation)",
        args_schema={
            "type": "object",
            "properties": {
                "service": {
                    "type": "string",
                    "description": "Service name to stop"
                }
            },
            "required": ["service"]
        },
        tier=ToolTier.SYSTEM_CHANGE,
        requires_confirmation=True,
        supports_dry_run=False,
        allows_network=False,
        timeout_sec=60,
        binary="/usr/bin/sudo",
        argv_template=["systemctl", "stop", "{service}"]
    )
    return CommandTool(spec)
