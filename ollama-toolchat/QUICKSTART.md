# Quick Start Guide

## Setup Steps

### 1. Install Dependencies

```bash
cd /mnt/local/Projects/SELOPC/ollama-toolchat
python3 -m venv venv
source venv/bin/activate
pip install -e .
```

### 2. Configure Environment

```bash
cp .env.example .env
nano .env  # Edit to match your system
```

**Important settings to customize:**
- `READ_ROOTS`: Directories you want the agent to read from
- `WRITE_ROOTS`: Directories you want the agent to write to (for photo organization)

### 3. Ensure Ollama is Running

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# If not running, start it
ollama serve

# Pull the model if needed
ollama pull llama3.1
```

### 4. Start the Application

```bash
source venv/bin/activate
python -m src.toolchat.main
```

### 5. Open the Web UI

Navigate to: http://127.0.0.1:8000

## First Commands to Try

1. **"How much free space do I have on my home directory?"**
2. **"What processes are using the most CPU?"**
3. **"What's making my computer slow?"**

## Security Notes

- The application only listens on localhost (127.0.0.1)
- All file operations are restricted to configured READ_ROOTS and WRITE_ROOTS
- Write operations require explicit confirmation
- Sensitive system directories are blocked by default

## Troubleshooting

**Can't connect to Ollama:**
```bash
ollama serve
```

**Permission errors:**
- Check your READ_ROOTS and WRITE_ROOTS in .env
- Ensure paths exist and are accessible

**Port already in use:**
- Change TOOLCHAT_PORT in .env to another port (e.g., 8001)

## Development

Run tests:
```bash
pytest tests/ -v
```

Check logs for debugging - the application uses structured JSON logging.
