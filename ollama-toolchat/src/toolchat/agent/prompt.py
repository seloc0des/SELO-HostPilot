def get_system_prompt() -> str:
    from ..tools.registry import registry
    
    tools = registry.list_tools()
    
    tool_descriptions = []
    for name, spec in tools.items():
        tier_label = "read-only" if spec.tier == 0 else ("write" if spec.tier == 1 else "system-change")
        confirmation = " (requires confirmation)" if spec.requires_confirmation else ""
        tool_descriptions.append(f"- {name}: {spec.description} [{tier_label}]{confirmation}")
    
    tools_section = "\n".join(tool_descriptions) if tool_descriptions else "- No tools currently registered"
    
    return f"""You are a friendly, helpful local PC assistant with access to system tools.

CONTEXT AWARENESS:
- Sometimes you'll be asked to call a tool (respond with JSON)
- Sometimes you'll receive tool results to explain (respond conversationally)
- Look at the conversation context to know which mode you're in

ABSOLUTE RULES - NEVER VIOLATE:
1. NEVER make up, guess, or hallucinate ANY system values (RAM, CPU, disk, temperature, etc.)
2. You do NOT know the user's system specs - you MUST call a tool to get real data
3. If the user asks about ANY system information, you MUST call the appropriate tool FIRST
4. Do NOT respond with system information unless you have JUST received tool results

CRITICAL TOOL MAPPINGS - MEMORIZE THESE:
- RAM/memory questions → ALWAYS use free_command or system_health (NEVER guess)
- CPU temperature questions → ALWAYS use sensors_command (NEVER system_health)
- GPU temperature questions → ALWAYS use gpu_temperature (NEVER sensors_command)
- CPU usage questions → ALWAYS use system_health or ps_command (NEVER guess)
- Disk space questions → ALWAYS use df_command (NEVER hallucinate)
- Filesystem questions → ALWAYS use lsblk_command (NEVER hallucinate)
- NEVER use gpu_temperature for CPU questions
- NEVER use sensors_command for GPU questions
- NEVER use system_health for temperature questions
- NEVER hallucinate disk information - ALWAYS call df_command
- NEVER hallucinate memory/RAM information - ALWAYS call free_command

IMPORTANT: You MUST use the exact tool names from this list. Do NOT make up tool names.

Available tools:
{tools_section}

RULES FOR TOOL USAGE:
1. When the user asks a question requiring system information, call the appropriate tool
2. Output ONLY this JSON format (no other text): {{"tool": "exact_tool_name", "args": {{}}, "explain": "what you're doing"}}
3. Use the EXACT tool name from the list above
4. Do NOT add any text before or after the JSON
5. Do NOT use markdown code blocks around the JSON

EXAMPLES:
User: "what is my ip address?"
You: {{"tool": "ip_addr_command", "args": {{}}, "explain": "Checking network interfaces and IP addresses"}}

User: "how much free space?"
You: {{"tool": "disk_free", "args": {{}}, "explain": "Checking available disk space"}}

User: "what is my current CPU temperature?"
You: {{"tool": "sensors_command", "args": {{}}, "explain": "Checking CPU core temperatures"}}

User: "what is my CPU temperature?"
You: {{"tool": "sensors_command", "args": {{}}, "explain": "Checking CPU core temperatures"}}

User: "CPU temperature?"
You: {{"tool": "sensors_command", "args": {{}}, "explain": "Checking CPU core temperatures"}}

User: "what is my current GPU temperature?"
You: {{"tool": "gpu_temperature", "args": {{}}, "explain": "Checking GPU temperature and utilization"}}

User: "what is my CPU usage?"
You: {{"tool": "system_health", "args": {{}}, "explain": "Checking CPU usage and system performance"}}

User: "how much RAM do I have?"
You: {{"tool": "free_command", "args": {{}}, "explain": "Checking memory usage"}}

User: "what is my memory status?"
You: {{"tool": "free_command", "args": {{}}, "explain": "Checking RAM usage"}}

User: "RAM usage?"
You: {{"tool": "free_command", "args": {{}}, "explain": "Checking memory status"}}

User: "what is my current disk space?"
You: {{"tool": "df_command", "args": {{}}, "explain": "Checking disk filesystem usage"}}

User: "what filesystems are mounted?"
You: {{"tool": "lsblk_command", "args": {{}}, "explain": "Listing block devices and mount points"}}

User: "show disk usage"
You: {{"tool": "df_command", "args": {{}}, "explain": "Checking disk filesystem usage"}}

AFTER TOOL EXECUTION (when you see tool results in a system message):
**CRITICAL: YOU ARE NOW IN CONVERSATION MODE - NOT TOOL CALLING MODE**

The system has already called the tool for you. You now have real data. Your ONLY job is to:
1. Read the data from the tool result
2. Craft a friendly, natural response explaining it to the user
3. Use the EXACT numbers but present them conversationally
4. Add helpful context ("that's normal", "looking good", "might want to check that", etc.)
5. Vary your phrasing - don't be repetitive

**ABSOLUTELY DO NOT:**
- Output JSON like {{"tool": "..."}}
- Try to call another tool
- Just repeat the raw data
- Use the same phrases every time
- NEVER output tool-call JSON after seeing tool results
- NEVER output {{"tool": "..."}} in your final response
- NEVER use JSON format when explaining results to the user

**EXAMPLES OF GOOD RESPONSES (DO NOT COPY THESE - CREATE YOUR OWN UNIQUE RESPONSES):**
These are ONLY examples to show the STYLE. Use the ACTUAL data from the tool results, not these example numbers.

Example style 1: "Your CPU's sitting pretty cool at 27.3°C right now - nothing to worry about there!"
Example style 2: "The RTX 4060 Ti is at 49°C with barely any load on it - nice and idle."
Example style 3: "You've got 44.9GB of RAM free out of 62.7GB total - plenty of headroom for whatever you're doing!"

**IMPORTANT: These are just to show conversational style. You MUST:**
- Use the REAL numbers from the actual tool result you just received
- Craft a UNIQUE response - don't repeat these examples word-for-word
- Vary your phrasing each time - be creative and natural
- Adapt your tone to the actual data (if temp is high, express concern; if it's low, be reassuring)

DATA INTEGRITY - CRITICAL:
- Use ONLY the EXACT numbers from the tool results - never round, estimate, or make up values
- If the tool says "27.3°C", say "27.3°C" - not "about 27°C" or "around 30°C"
- If the tool says "44.9GB", say "44.9GB" - not "about 45GB" or "nearly 45GB"
- NEVER add data that wasn't in the tool results
- NEVER guess or infer values - only report what the tool actually returned
- If you're unsure about a value, quote the tool output directly

YOUR PERSONALITY:
- You are a friendly, helpful local PC assistant
- Be conversational and natural - vary your responses, don't be robotic
- Add helpful context about what the numbers mean (e.g., "that's a healthy temperature" or "you might want to free up some space")
- Keep responses concise but warm - like a knowledgeable friend helping out
- Don't repeat the same phrases every time - mix up how you present information

EXAMPLE RESPONSES (vary your style, use EXACT numbers from results):
- "Your CPU is at 27.3°C right now - that's nice and cool, nothing to worry about!"
- "You've got 44.9GB of RAM free out of 62.7GB total - plenty of headroom there."
- "Your main drive is at 83% capacity with 37GB free - might be worth clearing out some old files soon."
- "The GPU's at 39°C with only 14% utilization - barely breaking a sweat."

COMMON TOOL MAPPINGS:
- IP address → ip_addr_command
- Disk space → disk_free or df_command  
- CPU temperature → sensors_command (NOT gpu_temperature)
- GPU temperature → gpu_temperature (NOT sensors_command)
- Memory → system_health or free_command
- CPU/processes → system_health or ps_command

IMPORTANT DISTINCTIONS:
- CPU temperature uses sensors_command to get CPU core temperatures
- GPU temperature uses gpu_temperature to get NVIDIA GPU data
- Do NOT use gpu_temperature for CPU temperature questions
- Do NOT use sensors_command for GPU temperature questions
"""


def format_tool_result(tool_name: str, result: dict) -> str:
    if result.get("ok"):
        data = result.get('data')
        
        # For any tool that returns stdout (command execution), show clean success message with relevant data
        if isinstance(data, dict) and 'stdout' in data:
            stdout = data.get('stdout', '')
            
            # Extract key information for specific tools
            if tool_name == 'ip_addr_command':
                # Extract IP addresses from stdout for the model to use
                import re
                ip_pattern = r'inet (\d+\.\d+\.\d+\.\d+/\d+)'
                ips = re.findall(ip_pattern, stdout)
                if ips:
                    # Filter out loopback and show primary IP first
                    primary_ips = [ip for ip in ips if not ip.startswith('127.')]
                    primary = primary_ips[0].split('/')[0] if primary_ips else None
                    return f"Primary IP: {primary}. All interfaces: {', '.join(ips)}"
                else:
                    return f"No IP addresses found on network interfaces."
            elif tool_name in ['df_command']:
                # Parse df output into user-friendly format
                lines = stdout.split('\n')
                storage_summary = []
                
                # Focus on main storage partitions (skip tmpfs, efivarfs, etc.)
                for line in lines[1:]:  # Skip header
                    if line and not line.startswith('tmpfs') and 'udev' not in line and 'efivarfs' not in line:
                        parts = line.split()
                        if len(parts) >= 6:
                            filesystem = parts[0]
                            size = parts[1]
                            used = parts[2]
                            avail = parts[3]
                            use_percent = parts[4]
                            mount = parts[5]
                            
                            # Convert to user-friendly descriptions
                            if mount == '/':
                                location = "main system (root)"
                            elif mount.startswith('/mnt/'):
                                location = f"storage at {mount}"
                            elif mount.startswith('/boot'):
                                location = "system boot partition"
                            else:
                                location = f"partition at {mount}"
                            
                            storage_summary.append(f"• {location}: {avail} free out of {size} total ({use_percent} used)")
                
                if storage_summary:
                    return "Disk space:\n" + "\n".join(storage_summary[:5])
                else:
                    return "No disk information found."
            elif tool_name == 'gpu_temperature':
                # GPU tool uses structured data, not stdout - this path shouldn't be hit
                # but handle it gracefully just in case
                return f"GPU information retrieved. Check structured data for details."
            elif tool_name == 'sensors_command':
                # Extract CPU temperature from sensors
                import re
                # Look for various CPU temperature patterns
                cpu_temps = []
                core_details = []
                
                # AMD CPU temps (k10temp)
                k10temp_temps = re.findall(r'Tctl:\s*\+(\d+(?:\.\d+)?)\s*°?C', stdout)
                if k10temp_temps:
                    cpu_temps.extend([float(t) for t in k10temp_temps])
                    core_details.extend([f"Tctl: {t}°C" for t in k10temp_temps])
                
                # Intel CPU temps (coretemp)
                core_temps = re.findall(r'(Core \d+):\s*\+(\d+(?:\.\d+)?)\s*°?C', stdout)
                if core_temps:
                    for core, temp in core_temps:
                        cpu_temps.append(float(temp))
                        core_details.append(f"{core}: {temp}°C")
                
                # Generic temp patterns
                generic_temps = re.findall(r'temp(\d+):\s*\+(\d+(?:\.\d+)?)\s*°?C', stdout)
                if generic_temps:
                    for temp_num, temp in generic_temps[:4]:  # Take first 4 temps
                        cpu_temps.append(float(temp))
                        core_details.append(f"Temp{temp_num}: {temp}°C")
                
                if cpu_temps:
                    avg_temp = sum(cpu_temps) / len(cpu_temps)
                    detail_str = f" ({', '.join(core_details[:3])})" if core_details else ""
                    return f"CPU temperature: {avg_temp:.1f}°C{detail_str}"
                else:
                    return "Could not read CPU temperature sensors."
            elif tool_name == 'free_command':
                # Parse free -h output for memory info
                lines = stdout.strip().split('\n')
                for line in lines:
                    if line.startswith('Mem:'):
                        parts = line.split()
                        if len(parts) >= 4:
                            total, used, free = parts[1], parts[2], parts[3]
                            available = parts[6] if len(parts) >= 7 else free
                            return f"RAM: {available} available, {used} used, {total} total"
                return f"Memory info:\n{stdout[:500]}"
            elif tool_name == 'lsblk_command':
                # Show block device summary
                lines = stdout.strip().split('\n')
                if len(lines) > 1:
                    devices = [l for l in lines[1:] if l.strip()][:10]
                    return f"Block devices retrieved ({len(devices)} shown):\n" + "\n".join(devices)
                return f"Block device information retrieved.\n{stdout[:500]}"
            elif tool_name == 'uptime_command':
                return f"Uptime: {stdout.strip()}"
            elif tool_name == 'uname_command':
                return f"System information: {stdout.strip()}"
            elif tool_name == 'hostname_command':
                return f"Hostname: {stdout.strip()}"
            elif tool_name == 'whoami_command':
                return f"Current user: {stdout.strip()}"
            elif tool_name == 'ps_command':
                # Show top processes summary
                lines = stdout.strip().split('\n')
                if len(lines) > 1:
                    header = lines[0]
                    procs = lines[1:11]  # Top 10 processes
                    return f"Processes ({len(lines)-1} total):\n{header}\n" + "\n".join(procs)
                return f"Process list:\n{stdout[:500]}"
            elif tool_name == 'top_command':
                # Show summary from top output
                lines = stdout.strip().split('\n')
                summary_lines = lines[:5] if len(lines) > 5 else lines
                return f"System load information:\n" + "\n".join(summary_lines)
            elif tool_name == 'du_command':
                # Show directory sizes
                lines = stdout.strip().split('\n')
                if lines:
                    entries = lines[-10:]  # Show last 10 (usually largest + total)
                    return f"Directory sizes:\n" + "\n".join(entries)
                return f"Directory size information retrieved."
            elif tool_name in ['journalctl_command', 'dmesg_command']:
                # Show recent log entries
                lines = stdout.strip().split('\n')
                recent = lines[-15:] if len(lines) > 15 else lines
                return f"Log entries retrieved ({len(lines)} lines, showing last {len(recent)}):\n" + "\n".join(recent)
            elif tool_name == 'ss_command':
                # Show socket/port info
                lines = stdout.strip().split('\n')
                if len(lines) > 1:
                    return f"Network connections ({len(lines)-1} entries):\n" + "\n".join(lines[:15])
                return f"Network connection information retrieved."
            elif tool_name in ['ping_command']:
                return f"Ping results:\n{stdout.strip()}"
            elif tool_name == 'findmnt_command':
                return f"Mount points:\n{stdout.strip()[:1000]}"
            elif tool_name in ['find_command', 'fd_command', 'rg_command']:
                lines = stdout.strip().split('\n')
                count = len([l for l in lines if l.strip()])
                preview = lines[:20]
                return f"Search results ({count} matches):\n" + "\n".join(preview)
            elif tool_name == 'tree_command':
                return f"Directory tree:\n{stdout.strip()[:1500]}"
            elif tool_name == 'vmstat_command':
                return f"Virtual memory statistics:\n{stdout.strip()}"
            elif tool_name == 'iostat_command':
                return f"I/O statistics:\n{stdout.strip()[:1500]}"
            elif tool_name == 'lspci_command':
                lines = stdout.strip().split('\n')
                return f"PCI devices ({len(lines)} entries):\n" + "\n".join(lines[:20])
            elif tool_name == 'lsusb_command':
                lines = stdout.strip().split('\n')
                return f"USB devices ({len(lines)} entries):\n" + "\n".join(lines[:15])
            elif tool_name == 'lscpu_command':
                return f"CPU information:\n{stdout.strip()}"
            elif tool_name == 'id_command':
                return f"User/Group IDs: {stdout.strip()}"
            elif tool_name == 'env_command':
                lines = stdout.strip().split('\n')
                return f"Environment variables ({len(lines)} total):\n" + "\n".join(lines[:20])
            elif tool_name == 'timedatectl_command':
                return f"Time and date info:\n{stdout.strip()}"
            elif tool_name == 'locale_command':
                return f"Locale settings:\n{stdout.strip()}"
            elif tool_name == 'htop_command':
                return f"htop version info: {stdout.strip()}"
            elif tool_name == 'pidstat_command':
                return f"Process statistics:\n{stdout.strip()[:1500]}"
            elif tool_name == 'iotop_command':
                return f"I/O by process:\n{stdout.strip()[:1500]}"
            elif tool_name == 'ip_route_command':
                return f"Routing table:\n{stdout.strip()}"
            elif tool_name == 'nmcli_command':
                return f"Network devices:\n{stdout.strip()}"
            elif tool_name == 'resolvectl_command':
                return f"DNS resolver status:\n{stdout.strip()[:1500]}"
            elif tool_name == 'ufw_status_command':
                return f"Firewall status:\n{stdout.strip()}"
            elif tool_name == 'aa_status_command':
                return f"AppArmor status:\n{stdout.strip()[:1500]}"
            elif tool_name == 'loginctl_command':
                return f"Login sessions:\n{stdout.strip()}"
            elif tool_name == 'lsof_command':
                lines = stdout.strip().split('\n')
                return f"Open files ({len(lines)} entries, showing first 20):\n" + "\n".join(lines[:20])
            elif tool_name == 'fuser_command':
                return f"File/socket usage:\n{stdout.strip()}"
            elif tool_name == 'file_command':
                return f"File type: {stdout.strip()}"
            elif tool_name == 'ldd_command':
                return f"Shared library dependencies:\n{stdout.strip()}"
            elif tool_name == 'last_command':
                return f"Recent logins:\n{stdout.strip()}"
            elif tool_name == 'systemctl_status':
                return f"Service status:\n{stdout.strip()}"
            elif tool_name == 'apt_install':
                return f"Package installation output:\n{stdout.strip()[:1500]}"
            elif tool_name == 'apt_update':
                return f"Package list update output:\n{stdout.strip()[:1500]}"
            elif tool_name == 'systemctl_restart':
                return f"Service restart completed.\n{stdout.strip()}" if stdout.strip() else "Service restart completed."
            elif tool_name == 'systemctl_start':
                return f"Service start completed.\n{stdout.strip()}" if stdout.strip() else "Service start completed."
            elif tool_name == 'systemctl_stop':
                return f"Service stop completed.\n{stdout.strip()}" if stdout.strip() else "Service stop completed."
            else:
                # Generic fallback: show truncated stdout instead of hiding it
                if stdout.strip():
                    truncated = stdout.strip()[:1000]
                    if len(stdout) > 1000:
                        truncated += "\n... (output truncated)"
                    return f"Command output:\n{truncated}"
                return f"Command executed successfully (no output)."
        elif isinstance(data, dict):
            # For structured data without stdout, show relevant summary
            if 'gpu_count' in data and 'gpus' in data:
                # Handle GPU temperature structured data
                gpus = data['gpus']
                if gpus:
                    gpu_info = []
                    for gpu in gpus:
                        temp = gpu.get('temperature_c', 'N/A')
                        util = gpu.get('utilization_percent', 'N/A')
                        mem_used = gpu.get('memory_used_mb', 'N/A')
                        mem_total = gpu.get('memory_total_mb', 'N/A')
                        power = gpu.get('power_draw_w', 'N/A')
                        name = gpu.get('name', 'GPU')
                        
                        # Format memory as GB if it's in MB
                        if mem_used != 'N/A' and mem_total != 'N/A':
                            try:
                                mem_used_gb = float(mem_used) / 1024
                                mem_total_gb = float(mem_total) / 1024
                                memory_info = f"{mem_used_gb:.1f}/{mem_total_gb:.1f}GB memory"
                            except (ValueError, TypeError):
                                memory_info = f"{mem_used}/{mem_total}MB memory"
                        else:
                            memory_info = "memory usage"
                        
                        details = []
                        if util != 'N/A':
                            details.append(f"{util}% utilization")
                        if memory_info:
                            details.append(memory_info)
                        if power != 'N/A':
                            details.append(f"{power}W power draw")
                        
                        detail_str = f" ({', '.join(details)})" if details else ""
                        gpu_info.append(f"{name}: {temp}°C{detail_str}")
                    
                    return "GPU: " + " | ".join(gpu_info)
                else:
                    return "No GPUs detected."
            elif 'memory_total_gb' in data and 'memory_used_gb' in data:
                # Handle system_health structured data
                memory_total = data.get('memory_total_gb', 'N/A')
                memory_used = data.get('memory_used_gb', 'N/A')
                memory_available = memory_total - memory_used if isinstance(memory_total, (int, float)) and isinstance(memory_used, (int, float)) else 'N/A'
                cpu_percent = data.get('cpu_percent', 'N/A')
                return f"CPU usage: {cpu_percent}%. RAM: {memory_available:.1f}GB available out of {memory_total:.1f}GB total."
            elif 'total_gb' in data and 'free_gb' in data:
                # Handle disk_free structured data
                path = data.get('path', 'disk')
                total = data.get('total_gb', 'N/A')
                free = data.get('free_gb', 'N/A')
                percent = data.get('percent_used', 'N/A')
                return f"Disk ({path}): {free:.1f}GB free out of {total:.1f}GB total ({percent:.1f}% used)"
            elif 'analyzed_path' in data and 'top_directories' in data:
                # Handle directory_size structured data
                analyzed = data.get('analyzed_path', 'N/A')
                depth = data.get('depth', 1)
                total = data.get('total_directories', 0)
                top_dirs = data.get('top_directories', [])
                
                if top_dirs:
                    dir_list = "\n".join([f"• {d['size']}\t{d['path']}" for d in top_dirs[:10]])
                    return f"Directory size analysis for {analyzed} (depth={depth}, {total} dirs):\n{dir_list}"
                return f"Directory size analysis completed for {analyzed}."
            elif 'dry_run' in data and 'total_photos' in data:
                # Handle organize_photos structured data
                dry_run = data.get('dry_run', True)
                total = data.get('total_photos', 0)
                message = data.get('message', '')
                
                if total == 0:
                    return "No photos found in the input directory."
                
                plan = data.get('plan', [])
                if plan:
                    preview = "\n".join([f"• {p['source']} → {p['destination']}" for p in plan[:5]])
                    return f"{message}\nPreview:\n{preview}"
                return message
            elif 'total' in data and 'free' in data:
                return f"Storage information: {data.get('free', 'N/A')} free out of {data.get('total', 'N/A')} total"
            elif 'exit_code' in data:
                return f"Operation completed successfully."
            else:
                return f"Tool '{tool_name}' completed successfully."
        else:
            return f"Tool '{tool_name}' completed successfully."
    else:
        return f"Tool '{tool_name}' failed. Error: {result.get('message')}"
