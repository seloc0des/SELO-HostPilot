import pytest
from src.toolchat.tools.cmd.command_tool import CommandTool, CommandToolSpec
from src.toolchat.tools.base import ToolTier


def test_command_tool_spec_creation():
    spec = CommandToolSpec(
        name="test_command",
        description="Test command",
        args_schema={"type": "object", "properties": {}},
        tier=ToolTier.READ_ONLY,
        binary="/usr/bin/echo",
        argv_template=["hello"]
    )
    
    assert spec.name == "test_command"
    assert spec.binary == "/usr/bin/echo"
    assert spec.argv_template == ["hello"]


def test_command_tool_build_command():
    spec = CommandToolSpec(
        name="test_command",
        description="Test command with args",
        args_schema={
            "type": "object",
            "properties": {
                "message": {"type": "string"}
            }
        },
        tier=ToolTier.READ_ONLY,
        binary="/usr/bin/echo",
        argv_template=["{message}"]
    )
    
    tool = CommandTool(spec)
    command = tool._build_command({"message": "hello world"})
    
    assert command == ["/usr/bin/echo", "hello world"]


def test_command_tool_execute_dry_run():
    spec = CommandToolSpec(
        name="test_command",
        description="Test command",
        args_schema={"type": "object", "properties": {}},
        tier=ToolTier.READ_ONLY,
        supports_dry_run=True,
        binary="/usr/bin/echo",
        argv_template=["test"]
    )
    
    tool = CommandTool(spec)
    result = tool.execute({}, dry_run=True)
    
    assert result.ok is True
    assert "command" in result.data
