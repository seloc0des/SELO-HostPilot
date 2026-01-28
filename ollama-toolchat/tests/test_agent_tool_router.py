import pytest
import json
from src.toolchat.agent.tool_router import ToolRouter


def test_parse_tool_call_valid():
    router = ToolRouter()
    
    response = '{"tool": "disk_free", "args": {"path": "/"}, "explain": "Check disk space"}'
    result = router.parse_tool_call(response)
    
    assert result is not None
    assert result["tool"] == "disk_free"
    assert result["args"]["path"] == "/"


def test_parse_tool_call_with_markdown():
    router = ToolRouter()
    
    response = '''```json
{"tool": "system_health", "args": {"limit": 5}, "explain": "Check system"}
```'''
    result = router.parse_tool_call(response)
    
    assert result is not None
    assert result["tool"] == "system_health"


def test_parse_tool_call_invalid():
    router = ToolRouter()
    
    response = "This is not a tool call"
    result = router.parse_tool_call(response)
    
    assert result is None


def test_parse_tool_call_missing_fields():
    router = ToolRouter()
    
    response = '{"tool": "disk_free"}'
    result = router.parse_tool_call(response)
    
    assert result is None


def test_execute_tool_not_found():
    router = ToolRouter()
    
    result, plan_id = router.execute_tool("nonexistent_tool", {}, "test_session")
    
    assert result.ok is False
    assert result.error_code == "tool_not_found"
    assert plan_id is None


def test_tool_alias_resolution():
    """Test that common command names resolve to their registered tool names."""
    from src.toolchat.tools.registry import registry, TOOL_ALIASES
    from src.toolchat.tools.base import BaseTool, ToolSpec, ToolResult, ToolTier
    
    # Create a mock tool to register
    class MockTool(BaseTool):
        def execute(self, args, dry_run=False):
            return ToolResult(ok=True, data={"mock": True})
    
    # Register a tool with the canonical name
    mock_spec = ToolSpec(
        name="fd_command",
        description="Test fd tool",
        args_schema={"type": "object", "properties": {}},
        tier=ToolTier.READ_ONLY,
        requires_confirmation=False,
        supports_dry_run=False,
        allows_network=False,
        timeout_sec=10,
    )
    mock_tool = MockTool(mock_spec)
    registry._tools["fd_command"] = mock_tool  # Direct assignment to avoid log spam
    
    # Test exact name lookup
    assert registry.get("fd_command") is not None
    assert registry.get("fd_command").spec.name == "fd_command"
    
    # Test alias lookup - "fd" should resolve to "fd_command"
    assert registry.get("fd") is not None
    assert registry.get("fd").spec.name == "fd_command"
    
    # Test that nonexistent aliases still return None
    assert registry.get("completely_fake_tool") is None
    
    # Verify common aliases are defined
    assert "fd" in TOOL_ALIASES
    assert TOOL_ALIASES["fd"] == "fd_command"
    assert "df" in TOOL_ALIASES
    assert TOOL_ALIASES["df"] == "df_command"
