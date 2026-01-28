"""Network inspection command tool specifications."""

from .command_tool import CommandTool, CommandToolSpec
from ..base import ToolTier


def create_ip_addr_tool():
    """Show IP addresses."""
    spec = CommandToolSpec(
        name="ip_addr_command",
        description="Display network interfaces and IP addresses",
        args_schema={"type": "object", "properties": {}},
        tier=ToolTier.READ_ONLY,
        requires_confirmation=False,
        supports_dry_run=False,
        allows_network=False,
        timeout_sec=5,
        binary="/usr/sbin/ip",
        argv_template=["addr", "show"]
    )
    return CommandTool(spec)


def create_ip_route_tool():
    """Show routing table."""
    spec = CommandToolSpec(
        name="ip_route_command",
        description="Display routing table",
        args_schema={"type": "object", "properties": {}},
        tier=ToolTier.READ_ONLY,
        requires_confirmation=False,
        supports_dry_run=False,
        allows_network=False,
        timeout_sec=5,
        binary="/usr/sbin/ip",
        argv_template=["route", "show"]
    )
    return CommandTool(spec)


def create_ss_tool():
    """Socket statistics."""
    spec = CommandToolSpec(
        name="ss_command",
        description="Show socket statistics (listening ports, connections). Use -tulpn for TCP/UDP listening ports.",
        args_schema={"type": "object", "properties": {}},
        tier=ToolTier.READ_ONLY,
        requires_confirmation=False,
        supports_dry_run=False,
        allows_network=False,
        timeout_sec=10,
        binary="/usr/bin/ss",
        argv_template=["-tulpn"]
    )
    return CommandTool(spec)


def create_nmcli_tool():
    """NetworkManager CLI."""
    spec = CommandToolSpec(
        name="nmcli_command",
        description="NetworkManager command-line interface for network device and connection info",
        args_schema={"type": "object", "properties": {}},
        tier=ToolTier.READ_ONLY,
        requires_confirmation=False,
        supports_dry_run=False,
        allows_network=False,
        timeout_sec=10,
        binary="/usr/bin/nmcli",
        argv_template=["dev", "status"]
    )
    return CommandTool(spec)


def create_ping_tool():
    """Ping network hosts."""
    spec = CommandToolSpec(
        name="ping_command",
        description="Test network connectivity to a host (limited to 3 packets for safety)",
        args_schema={
            "type": "object",
            "properties": {
                "host": {"type": "string", "description": "Host to ping"}
            },
            "required": ["host"]
        },
        tier=ToolTier.READ_ONLY,
        requires_confirmation=False,
        supports_dry_run=False,
        allows_network=True,
        timeout_sec=10,
        binary="/usr/bin/ping",
        argv_template=["-c", "3", "{host}"]
    )
    return CommandTool(spec)


def create_resolvectl_tool():
    """DNS resolver status."""
    spec = CommandToolSpec(
        name="resolvectl_command",
        description="Show DNS resolver status and configuration",
        args_schema={"type": "object", "properties": {}},
        tier=ToolTier.READ_ONLY,
        requires_confirmation=False,
        supports_dry_run=False,
        allows_network=False,
        timeout_sec=5,
        binary="/usr/bin/resolvectl",
        argv_template=["status"]
    )
    return CommandTool(spec)
