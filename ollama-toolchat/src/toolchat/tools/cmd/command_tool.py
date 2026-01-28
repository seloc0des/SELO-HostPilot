from typing import Dict, Any, List, Optional
import jsonschema
from pydantic import ConfigDict, Field
from ..base import BaseTool, ToolSpec, ToolResult, ToolTier
from ...infra.logging import get_logger
from .cmd_runner import command_runner

logger = get_logger(__name__)


class CommandToolSpec(ToolSpec):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    binary: str
    argv_template: List[str]
    default_args: Dict[str, Any] = Field(default_factory=dict)


class CommandTool(BaseTool):
    def __init__(self, spec: CommandToolSpec):
        super().__init__(spec)
        self.command_spec = spec
    
    def validate_args(self, args: Dict[str, Any]) -> bool:
        try:
            jsonschema.validate(instance=args, schema=self.spec.args_schema)
            return True
        except jsonschema.ValidationError as e:
            logger.error(f"Argument validation failed for {self.spec.name}: {e.message}")
            return False
    
    def _build_command(self, args: Dict[str, Any]) -> List[str]:
        command = [self.command_spec.binary]
        
        for template_arg in self.command_spec.argv_template:
            if template_arg.startswith("{") and template_arg.endswith("}"):
                arg_name = template_arg[1:-1]
                if arg_name in args:
                    value = str(args[arg_name])
                    command.append(value)
            else:
                command.append(template_arg)
        
        return command
    
    def execute(self, args: Dict[str, Any], dry_run: bool = False) -> ToolResult:
        if not self.validate_args(args):
            return ToolResult(
                ok=False,
                error_code="invalid_arguments",
                message=f"Invalid arguments for tool '{self.spec.name}'. Check the schema."
            )
        
        if dry_run and not self.spec.supports_dry_run:
            return ToolResult(
                ok=False,
                error_code="dry_run_not_supported",
                message=f"Tool '{self.spec.name}' does not support dry-run"
            )
        
        try:
            # Merge default args with provided args (provided args take precedence)
            merged_args = {**self.command_spec.default_args, **args}
            command = self._build_command(merged_args)
            
            logger.info(f"Executing command tool: {self.spec.name}", extra={
                "tool_name": self.spec.name,
                "command": " ".join(command),
            })
            
            if dry_run:
                return ToolResult(
                    ok=True,
                    data={
                        "command": " ".join(command),
                        "message": f"Would execute: {' '.join(command)}"
                    }
                )
            
            result = command_runner.run_command(
                command=command,
                timeout=self.spec.timeout_sec,
                allow_network=self.spec.allows_network,
                max_output_bytes=self.spec.max_output_bytes,
            )
            
            if result["ok"]:
                return ToolResult(
                    ok=True,
                    data={
                        "stdout": result["stdout"],
                        "exit_code": result["exit_code"],
                    }
                )
            else:
                return ToolResult(
                    ok=False,
                    error_code="command_failed",
                    message=f"Command failed: {result['stderr']}",
                    details=result
                )
        
        except Exception as e:
            logger.error(f"Command tool {self.spec.name} failed", exc_info=True)
            return ToolResult(
                ok=False,
                error_code="command_tool_error",
                message=f"Failed to execute command: {str(e)}"
            )
