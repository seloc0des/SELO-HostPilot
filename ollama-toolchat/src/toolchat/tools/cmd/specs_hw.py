from ..base import ToolTier
from .command_tool import CommandTool, CommandToolSpec


def create_lspci_tool() -> CommandTool:
    spec = CommandToolSpec(
        name="lspci_command",
        description="List all PCI devices",
        args_schema={
            "type": "object",
            "properties": {}
        },
        tier=ToolTier.READ_ONLY,
        requires_confirmation=False,
        supports_dry_run=False,
        allows_network=False,
        timeout_sec=10,
        binary="/usr/bin/lspci",
        argv_template=["-v"]
    )
    return CommandTool(spec)


def create_lsusb_tool() -> CommandTool:
    spec = CommandToolSpec(
        name="lsusb_command",
        description="List USB devices",
        args_schema={
            "type": "object",
            "properties": {}
        },
        tier=ToolTier.READ_ONLY,
        requires_confirmation=False,
        supports_dry_run=False,
        allows_network=False,
        timeout_sec=10,
        binary="/usr/bin/lsusb",
        argv_template=["-v"]
    )
    return CommandTool(spec)


def create_lscpu_tool() -> CommandTool:
    spec = CommandToolSpec(
        name="lscpu_command",
        description="Display CPU architecture information",
        args_schema={
            "type": "object",
            "properties": {}
        },
        tier=ToolTier.READ_ONLY,
        requires_confirmation=False,
        supports_dry_run=False,
        allows_network=False,
        timeout_sec=5,
        binary="/usr/bin/lscpu",
        argv_template=[]
    )
    return CommandTool(spec)


def create_sensors_tool() -> CommandTool:
    spec = CommandToolSpec(
        name="sensors_command",
        description="Show hardware sensor information (temperature, fans, voltage)",
        args_schema={
            "type": "object",
            "properties": {}
        },
        tier=ToolTier.READ_ONLY,
        requires_confirmation=False,
        supports_dry_run=False,
        allows_network=False,
        timeout_sec=10,
        binary="/usr/bin/sensors",
        argv_template=[]
    )
    return CommandTool(spec)
