# SELO HostPilot

SELOdev’s **local-first host control companion** built for Pop!_OS. SELO HostPilot delivers a responsive web UI for natural language conversations, safe system tooling, and guided automation under your control.

## Features

- 🤖 **Natural Language Interface** - Talk to your host using everyday language
- 🔒 **Security First** - Sandboxed execution with strict path controls, confirmation gates, and auditing
- 🛠️ **Extensive Tool Library** - 49 curated system utilities plus Python-native helpers from SELOdev's tool registry
- 🌐 **Local-Only** - SELO HostPilot runs entirely on your machine with no outbound data
- 📊 **System Diagnostics** - Deep insights across disk, CPU, memory, processes, logs, and hardware sensors
- 📸 **Photo Organization** - Automatically regroup photos by date with exiftool + Pillow fallbacks
- � **Duplicate File Finder** - Find and report duplicate files using content hashing
- � **Persistent History** - SQLite-backed conversation storage in `ollama-toolchat.db`
- 📝 **Audit Logging** - Full audit trail in `ollama-toolchat-audit.db` for every tool execution
- 🎯 **Dynamic Model Selection** - Swap Ollama models instantly from the web header
- ⚡ **Smart Auto-Responses** - Instant answers for common questions about capabilities without LLM latency

## Architecture

Brought to life by the Software Design Document (SDD), the SELOdev stack consists of:

- **Web UI** - Modern, responsive chat interface
- **FastAPI Backend** - RESTful API with session management
- **Ollama Integration** - Local LLM inference
- **Tool System** - Modular, registry-based tool execution
- **Security Layer** - Path validation, sandboxing, and permission tiers
- **Confirmation Protocol** - Two-step commit for write operations

## Prerequisites

- **Pop!_OS** (or Ubuntu-based Linux)
- **Python 3.11+**
- **Ollama** installed and running locally
- **qwen2.5:7b** model (the only model that has been tested and verified to work)

### Install Ollama

```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull qwen2.5:7b
```

### Optional System Tools (Recommended)

For enhanced capabilities, install these tools:

```bash
sudo apt update
sudo apt install -y htop sysstat ncdu lm-sensors smartmontools exiftool imagemagick ffmpeg
```

**Tool Benefits:**
- `sysstat` - Enables iostat for I/O statistics
- `lm-sensors` - Enables temperature and fan monitoring
- `exiftool` - Best-in-class photo metadata extraction
- `smartmontools` - Drive health monitoring (future feature)
- `imagemagick` - Image manipulation (future feature)
- `ffmpeg` - Video processing (future feature)

## Installation

1. **Clone or navigate to the project directory:**

```bash
cd /mnt/local/Projects/SELO-HostPilot/ollama-toolchat
```

2. **Create a virtual environment:**

```bash
python3 -m venv venv
source venv/bin/activate
```

3. **Install dependencies:**

```bash
pip install -e .
```

4. **Configure environment:**

```bash
cp .env.example .env
```

Edit `.env` to match your system. The `.env.example` file already contains placeholder values (see `/home/<your-user>` and the standard Ollama defaults) so you only need to update paths, hostnames, or sandbox settings that differ from your machine.

**Important:** Replace every `/home/<your-user>` placeholder with your actual home directory before starting the server and ensure `READ_ROOTS`/`WRITE_ROOTS` list only directories you want the assistant to access.

## Usage

### Start the Server

```bash
cd /mnt/local/Projects/SELOPC/ollama-toolchat
source venv/bin/activate
python -m src.toolchat.main
```

Or using uvicorn directly:

```bash
uvicorn src.toolchat.main:app --host 127.0.0.1 --port 8000
```

### Access the Web UI

Open your browser and navigate to:

```
http://127.0.0.1:8000
```

### Change the Model

You can change the Ollama model in two ways:

**1. Via Web UI:**
- Use the model selector dropdown in the header
- Select from available models
- **Important:** Only `qwen2.5:7b` has been tested and verified to work properly
- The change takes effect immediately for new conversations

**2. Via Environment Variable:**
- Set `OLLAMA_MODEL` in your `.env` file
- Restart the server for changes to take effect

### Example Interactions

**Check disk space:**
```
User: How much free space do I have on my home directory?
Assistant: [Uses disk_free tool to check /home]
```

**Monitor system health:**
```
User: What's making my computer slow?
Assistant: [Uses system_health tool to analyze CPU and memory]
```

**Organize photos:**
```
User: Organize my photos in ~/Pictures/Inbox by month
Assistant: [Proposes plan with dry-run results]
User: [Clicks Confirm button]
Assistant: [Executes the photo organization]
```

**Get help with capabilities:**
```
User: what can you do?
Assistant: [Instant response with comprehensive feature overview]
```

**Find duplicate files:**
```
User: Find duplicate files in /mnt/local/Projects
Assistant: [Scans directory and reports duplicate groups with wasted space]
```

## Smart Auto-Responses

SELO HostPilot includes intelligent auto-response functionality that provides instant answers to common questions about capabilities without requiring LLM inference. This ensures faster responses and consistent information.

### Supported Auto-Response Queries

The system automatically detects and responds to questions such as:

- "what can you do", "what do you do", "what are your capabilities"
- "help", "features", "commands", "tools"
- "what can you help me with", "how can you help"
- "what should i ask you", "what kind of questions"
- "what's your purpose", "what are you for"

### Auto-Response Content

When triggered, the system provides a comprehensive overview including:

**System Monitoring:**
- CPU usage, temperature, and process monitoring
- Memory/RAM usage analysis
- GPU temperature and usage tracking
- System uptime and hardware information

**Storage & Files:**
- Disk space and usage analysis
- Photo organization by date (with confirmation)
- Directory size analysis
- Filesystem and mount information

**Network:**
- IP address and network interface information
- Network status and connection monitoring
- Listening ports and routing information

**Hardware & Logs:**
- Hardware device enumeration (PCI/USB)
- System sensors and temperature monitoring
- System logs and kernel message access

**Security First:**
- Confirmation requirements for safety
- Sandboxed execution with path controls
- Full audit logging of all actions

### Benefits

- **⚡ Instant Response** - No LLM latency for common questions
- **📚 Consistent Information** - Always provides accurate, up-to-date capability descriptions
- **🔧 Resource Efficient** - Saves Ollama API calls for frequent questions
- **🗣️ User Friendly** - Natural language matching with case insensitivity
- **🔄 Maintainable** - Easy to add new patterns and response types

## Available Tools

### Python-Native Tools (MVP)

#### 1. disk_free (Tier 0 - Read-Only)
Check free disk space for a given path using Python's shutil.

**Example:** "How much space is free on /home?"

#### 2. system_health (Tier 0 - Read-Only)
Check CPU, memory usage, and top processes using psutil.

**Example:** "What processes are using the most CPU?"

#### 3. organize_photos (Tier 1 - Write Safe)
Organize photos into directories by date taken. Uses exiftool when available, falls back to Pillow. Requires confirmation.

**Example:** "Organize photos in ~/Pictures/Inbox by year and month"

#### 4. find_duplicates (Tier 0 - Read-Only)
Find duplicate files in a directory by comparing file hashes. Uses a two-pass algorithm (size grouping + MD5 hashing) for efficiency.

**Example:** "Find duplicate files in /mnt/local/Projects"

#### 5. directory_size (Tier 0 - Read-Only)
Analyze directory sizes to find which directories are taking up the most space.

**Example:** "How big is /home/sean/Downloads?"

#### 6. gpu_temperature (Tier 0 - Read-Only)
Check NVIDIA GPU temperature and utilization using nvidia-smi.

**Example:** "What's my GPU temperature?"

### Command Tools (System Utilities)

#### Storage Tools (Tier 0)
- **df_command** - Filesystem disk space usage
- **du_command** - Directory disk usage estimation
- **lsblk_command** - List block devices
- **findmnt_command** - Find mounted filesystems

#### Performance Tools (Tier 0)
- **ps_command** - Process status information
- **free_command** - Memory usage statistics
- **vmstat_command** - Virtual memory statistics
- **iostat_command** - CPU and I/O statistics (requires sysstat)
- **uptime_command** - System uptime and load averages

#### Log Tools (Tier 0)
- **journalctl_command** - Query systemd journal logs
- **dmesg_command** - Kernel ring buffer messages

#### Hardware Tools (Tier 0)
- **lspci_command** - List PCI devices
- **lsusb_command** - List USB devices
- **lscpu_command** - CPU architecture information
- **sensors_command** - Hardware sensor readings (requires lm-sensors)

#### File Search Tools (Tier 0)
- **fd_command** - Fast file finder (modern alternative to find)
- **find_command** - Search for files and directories
- **rg_command** - Search file contents using ripgrep
- **tree_command** - Display directory structure as a tree

#### Network Tools (Tier 0)
- **ip_addr_command** - Show IP addresses and network interfaces
- **ip_route_command** - Show routing table
- **ss_command** - Show socket statistics
- **ping_command** - Test network connectivity
- **nmcli_command** - NetworkManager CLI
- **resolvectl_command** - DNS resolver status

#### Security Tools (Tier 0)
- **ufw_status_command** - Firewall status
- **aa_status_command** - AppArmor status
- **loginctl_command** - Login session information

#### System Info Tools (Tier 0)
- **uname_command** - System information
- **hostname_command** - System hostname
- **whoami_command** - Current user
- **uptime_command** - System uptime and load

**Note:** Command tools are automatically registered if the underlying system utilities are available.

## Security Model

### Permission Tiers

- **Tier 0 (Read-Only):** Safe diagnostic commands (disk usage, process lists)
- **Tier 1 (Write Safe):** Scoped file operations within allowed write roots
- **Tier 2 (System Change):** Package installs, service restarts (not implemented in MVP)

### Path Controls

- **READ_ROOTS:** Directories the agent can read from
- **WRITE_ROOTS:** Directories the agent can modify
- **Denied Paths:** `/etc`, `/boot`, `/root`, `/var/lib`, `/usr`, `~/.ssh`

### Sandbox Modes

- **none:** Direct execution with path validation (MVP default)
- **systemd:** Use systemd-run for resource limits and isolation
- **bwrap:** Use bubblewrap for namespace isolation

To enable sandboxing, set `SANDBOX_MODE=systemd` or `SANDBOX_MODE=bwrap` in `.env`.

### Confirmation Protocol

Write operations (Tier 1+) require explicit user confirmation:

1. Tool executes in dry-run mode
2. User sees preview of changes
3. User clicks "Confirm" or "Cancel"
4. Action executes only after confirmation

## Development

### Run Tests

```bash
pytest tests/
```

### Project Structure

```
ollama-toolchat/
├── src/toolchat/
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration management
│   ├── api/                 # API routes
│   ├── agent/               # LLM agent logic
│   ├── tools/               # Tool implementations
│   └── infra/               # Infrastructure (logging, security, sandbox)
├── web/                     # Frontend UI
├── tests/                   # Test suite
├── pyproject.toml           # Dependencies
└── README.md
```

### Adding New Tools

1. Create a new tool class inheriting from `BaseTool`
2. Define the tool specification (name, description, args schema, tier)
3. Implement the `execute` method
4. Register the tool in `main.py`

Example:

```python
from .base import BaseTool, ToolSpec, ToolResult, ToolTier

class MyTool(BaseTool):
    def __init__(self):
        spec = ToolSpec(
            name="my_tool",
            description="Does something useful",
            args_schema={"type": "object", "properties": {...}},
            tier=ToolTier.READ_ONLY,
        )
        super().__init__(spec)
    
    def execute(self, args, dry_run=False):
        # Implementation
        return ToolResult(ok=True, data={"result": "success"})
```

## New Features

### SQLite Persistence

Chat history is now automatically saved to `ollama-toolchat.db`:
- Conversations persist across restarts
- Session management with timestamps
- Automatic fallback to in-memory if database unavailable

### Audit Logging

All tool executions are logged to `ollama-toolchat-audit.db`:
- Complete audit trail of all actions
- Tracks tool name, tier, arguments, results
- Records user confirmations
- Timestamps and correlation IDs

### Enhanced Photo Organization

The photo organizer now:
- Uses exiftool when available for better EXIF reading
- Falls back to Pillow for compatibility
- Handles filename collisions automatically
- Supports multiple date formats

### Command Tool System

49 system commands safely wrapped:
- Automatic binary path resolution
- Safe argument templating
- Output truncation and timeouts
- Graceful degradation if tools unavailable

### Tool Name Aliases

The system supports natural tool name aliases, so you can use common command names:
- `fd` → `fd_command`
- `find` → `find_command`
- `df` → `df_command`
- `tree` → `tree_command`
- `duplicates` → `find_duplicates`
- And 50+ more aliases

This means the LLM can use familiar command names and the system will resolve them to the correct registered tool.

### Duplicate File Finder

The `find_duplicates` tool uses an efficient two-pass algorithm:
1. **Size grouping** - Files are first grouped by size (potential duplicates)
2. **Quick hash** - Files with matching sizes are hashed (first 8KB + size)
3. **Full verification** - Matching quick hashes are verified with full MD5

Features:
- Scans up to 10,000 files with configurable depth
- Skips common non-content directories (`.git`, `node_modules`, `__pycache__`)
- Reports wasted space and top duplicate groups
- Minimum file size filter to skip tiny files

## API Endpoints

### POST /v1/chat/send
Send a message to the chatbot.

**Request:**
```json
{
  "session_id": "optional-uuid",
  "message": "How much disk space is free?"
}
```

**Response:**
```json
{
  "session_id": "uuid",
  "reply": "You have 50GB free on /home",
  "pending_confirmation": false,
  "plan_id": null
}
```

### POST /v1/chat/confirm
Confirm a pending action.

**Request:**
```json
{
  "session_id": "uuid",
  "plan_id": "pln_...",
  "confirm": true
}
```

**Response:**
```json
{
  "reply": "Action completed successfully"
}
```

### GET /v1/health
Health check endpoint.

**Response:**
```json
{
  "status": "ok"
}
```

### GET /v1/model
Get the currently active Ollama model.

**Response:**
```json
{
  "model": "llama3.1"
}
```

### POST /v1/model
Change the active Ollama model.

**Request:**
```json
{
  "model": "mistral"
}
```

**Response:**
```json
{
  "model": "mistral",
  "message": "Model changed to mistral"
}
```

**Note:** The model must be already pulled in Ollama. Use `ollama pull <model>` to download models. **Warning:** Only `qwen2.5:7b` has been tested and verified to work with this system. Other models may not function correctly.

## Model Compatibility

**⚠️ IMPORTANT:** This project has only been tested and verified to work with the **qwen2.5:7b** model. While the system allows you to select other Ollama models, we cannot guarantee their compatibility or proper functionality.

### Why qwen2.5:7b?

- **Tool Usage:** qwen2.5:7b demonstrates reliable understanding and execution of the tool system
- **Safety:** The model respects the confirmation protocol and security boundaries
- **Performance:** Optimal balance of capability and resource usage for local deployment
- **Reliability:** Consistent behavior in following system commands and constraints

### Using Other Models

If you choose to use other models:
1. They may not understand the tool system correctly
2. Safety protocols might be ignored
3. Tool execution may fail or behave unexpectedly
4. The confirmation protocol may not work as intended

**Recommendation:** Stick with `qwen2.5:7b` for the best experience.

## Troubleshooting

### Ollama Connection Error

Ensure Ollama is running:
```bash
ollama serve
```

Check the model is available:
```bash
ollama list
```

### Permission Denied Errors

Verify your `READ_ROOTS` and `WRITE_ROOTS` in `.env` include the paths you're trying to access.

### Tool Not Working

Check the logs for detailed error messages. The application uses structured JSON logging.

## Roadmap

- [ ] Additional system diagnostic tools
- [ ] Network tools (with explicit opt-in)
- [ ] Custom tool configuration via YAML
- [ ] Integration tests for streaming endpoint
- [ ] OpenAPI/Swagger documentation enhancements

## License

SELO HostPilot is open source under the MIT License. See [LICENSE](LICENSE) for the full terms.

## Contributing

This is a local-first tool designed for personal use on Pop!_OS. Contributions should maintain the security-first approach and local-only operation model.

## Support

For issues or questions, refer to the Software Design Document or check the application logs.
