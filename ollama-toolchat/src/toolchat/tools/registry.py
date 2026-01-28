from typing import Dict, Optional
from .base import BaseTool, ToolSpec
from ..infra.logging import get_logger

logger = get_logger(__name__)

# Aliases for common command names that models might use instead of registered names
# Maps common/short names to the actual registered tool names
TOOL_ALIASES: Dict[str, str] = {
    # File search tools
    "fd": "fd_command",
    "find": "find_command",
    "rg": "rg_command",
    "ripgrep": "rg_command",
    "tree": "tree_command",
    # Storage tools
    "df": "df_command",
    "du": "du_command",
    "lsblk": "lsblk_command",
    "findmnt": "findmnt_command",
    # Performance tools
    "ps": "ps_command",
    "free": "free_command",
    "vmstat": "vmstat_command",
    "uptime": "uptime_command",
    "iostat": "iostat_command",
    "top": "top_command",
    "htop": "htop_command",
    "pidstat": "pidstat_command",
    "iotop": "iotop_command",
    # Log tools
    "journalctl": "journalctl_command",
    "dmesg": "dmesg_command",
    # Hardware tools
    "lspci": "lspci_command",
    "lsusb": "lsusb_command",
    "lscpu": "lscpu_command",
    "sensors": "sensors_command",
    # System info tools
    "uname": "uname_command",
    "hostname": "hostname_command",
    "whoami": "whoami_command",
    "id": "id_command",
    "env": "env_command",
    "timedatectl": "timedatectl_command",
    "locale": "locale_command",
    # Network tools
    "ip_addr": "ip_addr_command",
    "ip_route": "ip_route_command",
    "ss": "ss_command",
    "nmcli": "nmcli_command",
    "ping": "ping_command",
    "resolvectl": "resolvectl_command",
    # Security tools
    "ufw_status": "ufw_status_command",
    "ufw": "ufw_status_command",
    "aa_status": "aa_status_command",
    "apparmor": "aa_status_command",
    "loginctl": "loginctl_command",
    # Power user tools
    "lsof": "lsof_command",
    "fuser": "fuser_command",
    "file": "file_command",
    "ldd": "ldd_command",
    "last": "last_command",
    # System management
    "systemctl": "systemctl_status",
    "apt_install": "apt_install",
    "apt_update": "apt_update",
    # File utilities
    "duplicates": "find_duplicates",
    "find_dups": "find_duplicates",
}


class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}
    
    def register(self, tool: BaseTool) -> None:
        self._tools[tool.spec.name] = tool
        logger.info(f"Registered tool: {tool.spec.name} (tier={tool.spec.tier})")
    
    def get(self, name: str) -> Optional[BaseTool]:
        # Try exact match first
        tool = self._tools.get(name)
        if tool:
            return tool
        
        # Try alias lookup
        canonical_name = TOOL_ALIASES.get(name)
        if canonical_name:
            tool = self._tools.get(canonical_name)
            if tool:
                logger.info(f"Resolved tool alias '{name}' to '{canonical_name}'")
                return tool
        
        return None
    
    def list_tools(self) -> Dict[str, ToolSpec]:
        return {name: tool.spec for name, tool in self._tools.items()}
    
    def get_tool_descriptions(self) -> list:
        tools = []
        for name, tool in self._tools.items():
            tools.append({
                "name": tool.spec.name,
                "description": tool.spec.description,
                "parameters": tool.spec.args_schema,
            })
        return tools


registry = ToolRegistry()
