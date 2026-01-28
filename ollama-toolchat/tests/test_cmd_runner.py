import pytest
from src.toolchat.tools.cmd.cmd_runner import CommandRunner


def test_command_runner_simple_command():
    runner = CommandRunner()
    
    result = runner.run_command(
        command=["echo", "hello"],
        timeout=5
    )
    
    assert result["ok"] is True
    assert "hello" in result["stdout"]


def test_command_runner_timeout():
    runner = CommandRunner()
    
    result = runner.run_command(
        command=["sleep", "10"],
        timeout=1
    )
    
    assert result["ok"] is False
    assert "timed out" in result["stderr"].lower()


def test_command_runner_invalid_command():
    runner = CommandRunner()
    
    result = runner.run_command(
        command=["nonexistent_command_xyz"],
        timeout=5
    )
    
    assert result["ok"] is False
