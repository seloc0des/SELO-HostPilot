"""
Query classifier to detect system-related questions that MUST use tools.
This prevents the LLM from hallucinating system information.
"""

import re
from typing import Optional, Tuple
from ..infra.logging import get_logger

logger = get_logger(__name__)


# Patterns that indicate system queries requiring tool calls
SYSTEM_QUERY_PATTERNS = {
    # Memory/RAM patterns - be specific about what user wants
    "how much memory": "free_command",
    "how much ram": "free_command",
    "available memory": "free_command",
    "available ram": "free_command",
    "free memory": "free_command",
    "free ram": "free_command",
    "total memory": "free_command",
    "total ram": "free_command",
    # Process/usage patterns - what's using RAM
    "using ram": "ps_command",
    "using memory": "ps_command",
    "utilizing ram": "ps_command",
    "utilizing memory": "ps_command",
    "memory usage by process": "ps_command",
    "ram usage by process": "ps_command",
    "processes using": "ps_command",
    "services using": "ps_command",
    
    # CPU patterns
    "cpu temperature": "sensors_command",
    "cpu temp": "sensors_command",
    "processor temperature": "sensors_command",
    "cpu usage": "system_health",
    "cpu utilization": "system_health",
    "processor usage": "system_health",
    
    # GPU patterns
    "gpu temperature": "gpu_temperature",
    "gpu temp": "gpu_temperature",
    "graphics card temp": "gpu_temperature",
    "nvidia temp": "gpu_temperature",
    "gpu usage": "gpu_temperature",
    "gpu utilization": "gpu_temperature",
    
    # Disk patterns
    "disk space": "df_command",
    "disk usage": "df_command",
    "storage space": "df_command",
    "free space": "df_command",
    "how much space": "df_command",
    "available space": "df_command",
    "filesystem": "lsblk_command",
    "filesystems": "lsblk_command",
    "mounted": "findmnt_command",
    "mount points": "findmnt_command",
    "block devices": "lsblk_command",
    
    # Network patterns
    "ip address": "ip_addr_command",
    "my ip": "ip_addr_command",
    "network interface": "ip_addr_command",
    "what is my ip": "ip_addr_command",
    "network status": "nmcli_command",
    "network connection": "nmcli_command",
    "routing table": "ip_route_command",
    "listening ports": "ss_command",
    "open ports": "ss_command",
    "dns": "resolvectl_command",
    
    # System info patterns
    "uptime": "uptime_command",
    "how long running": "uptime_command",
    "system uptime": "uptime_command",
    "hostname": "hostname_command",
    "kernel": "uname_command",
    "os version": "uname_command",
    "system info": "uname_command",
    "who am i": "whoami_command",
    "current user": "whoami_command",
    "username": "whoami_command",
    
    # Process patterns
    "running processes": "ps_command",
    "process list": "ps_command",
    "top processes": "top_command",
    "what's running": "ps_command",
    
    # Hardware patterns
    "pci devices": "lspci_command",
    "usb devices": "lsusb_command",
    "hardware": "lspci_command",
    "sensors": "sensors_command",
    "temperature": "sensors_command",
    
    # Log patterns
    "system logs": "journalctl_command",
    "journal": "journalctl_command",
    "dmesg": "dmesg_command",
    "kernel messages": "dmesg_command",
}

# Patterns that trigger auto-responses (no LLM call needed)
AUTO_RESPONSE_PATTERNS = {
    "what can you do": "capabilities",
    "what do you do": "capabilities", 
    "what are your capabilities": "capabilities",
    "what are you capable of": "capabilities",
    "what can you help me with": "capabilities",
    "help": "capabilities",
    "commands": "capabilities",
    "tools": "capabilities",
    "features": "capabilities",
    "what tools do you have": "capabilities",
    "what are your features": "capabilities",
    "what functionality do you have": "capabilities",
    "what can i ask you": "capabilities",
    "what should i ask you": "capabilities",
    "what kind of questions": "capabilities",
    "how can you help": "capabilities",
    "what's your purpose": "capabilities",
    "what are you for": "capabilities",
    "what do you do exactly": "capabilities",
}

# Auto-response content
AUTO_RESPONSES = {
    "capabilities": """I'm SELO HostPilot, your local system control companion! Here's what I can help you with:

**System Monitoring:**
- Check CPU usage, temperature, and processes
- Monitor memory/RAM usage and what's using it
- Check GPU temperature and usage
- View system uptime and hardware info

**Storage & Files:**
- Check disk space and usage
- Organize photos by date (with confirmation)
- Directory size analysis
- Filesystem and mount information

**Network:**
- Check IP addresses and network interfaces
- View network status and connections
- Check listening ports and routing

**Hardware & Logs:**
- View hardware devices (PCI/USB)
- Check system sensors and temperatures
- Read system logs and kernel messages

**Security First:**
- All operations require confirmation for safety
- Sandboxed execution with path controls
- Full audit logging of all actions

Just ask me naturally like "How much disk space do I have?" or "What's using my RAM?" and I'll take care of the rest!""",
}


def classify_query(query: str) -> Tuple[bool, Optional[str]]:
    """
    Classify a user query to determine if it requires a tool call.
    
    Returns:
        Tuple of (requires_tool, suggested_tool_name)
        - requires_tool: True if this query MUST use a tool
        - suggested_tool_name: The tool that should be used, or None
    """
    query_lower = query.lower().strip()
    
    # Check auto-response patterns first
    for pattern, response_type in AUTO_RESPONSE_PATTERNS.items():
        if pattern in query_lower:
            logger.info(f"Query classified as auto-response: pattern='{pattern}' -> response='{response_type}'")
            return True, f"auto_response:{response_type}"
    
    # Check each pattern
    for pattern, tool_name in SYSTEM_QUERY_PATTERNS.items():
        if pattern in query_lower:
            logger.info(f"Query classified as system query: pattern='{pattern}' -> tool='{tool_name}'")
            return True, tool_name
    
    # Additional regex patterns for more complex matching
    regex_patterns = [
        # "how much X do I have" patterns
        (r"how much (ram|memory|disk|space|storage)", "free_command"),
        (r"what('s| is) my (ram|memory)", "free_command"),
        (r"(check|show|get|display) (my )?(ram|memory)", "free_command"),
        (r"(check|show|get|display) (my )?(cpu|processor) (temp|temperature)", "sensors_command"),
        (r"(check|show|get|display) (my )?(gpu|graphics) (temp|temperature)", "gpu_temperature"),
        (r"(check|show|get|display) (my )?(disk|storage) (space|usage)", "df_command"),
        (r"(check|show|get|display) (my )?ip", "ip_addr_command"),
        (r"what('s| is) (the )?(cpu|processor) (temp|temperature)", "sensors_command"),
        (r"what('s| is) (the )?(gpu|graphics) (temp|temperature)", "gpu_temperature"),
    ]
    
    for pattern, tool_name in regex_patterns:
        if re.search(pattern, query_lower):
            logger.info(f"Query classified as system query (regex): pattern='{pattern}' -> tool='{tool_name}'")
            return True, tool_name
    
    return False, None


def requires_tool_call(query: str) -> bool:
    """Check if a query requires a tool call (simpler interface)."""
    requires, _ = classify_query(query)
    return requires


def get_suggested_tool(query: str) -> Optional[str]:
    """Get the suggested tool for a query, or None if no tool is needed."""
    _, tool = classify_query(query)
    return tool


def is_auto_response(query: str) -> bool:
    """Check if a query should trigger an auto-response."""
    query_lower = query.lower().strip()
    
    for pattern in AUTO_RESPONSE_PATTERNS.keys():
        if pattern in query_lower:
            return True
    
    return False


def get_auto_response(query: str) -> Optional[str]:
    """Get the auto-response for a query, or None if no auto-response is defined."""
    query_lower = query.lower().strip()
    
    for pattern, response_type in AUTO_RESPONSE_PATTERNS.items():
        if pattern in query_lower:
            return AUTO_RESPONSES.get(response_type)
    
    return None


def get_auto_response_type(query: str) -> Optional[str]:
    """Get the auto-response type for a query, or None if no auto-response is defined."""
    query_lower = query.lower().strip()
    
    for pattern, response_type in AUTO_RESPONSE_PATTERNS.items():
        if pattern in query_lower:
            return response_type
    
    return None
