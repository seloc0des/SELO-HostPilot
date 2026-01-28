from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from ..config import settings
from ..infra.logging import get_logger
from pathlib import Path

logger = get_logger(__name__)

router = APIRouter()


class SettingsResponse(BaseModel):
    ollama_url: str
    ollama_model: str
    read_roots: List[str]
    write_roots: List[str]
    sandbox_mode: str
    allow_network: bool
    log_level: str


class SettingsUpdateRequest(BaseModel):
    ollama_url: str
    ollama_model: str
    read_roots: List[str]
    write_roots: List[str]
    sandbox_mode: str
    allow_network: bool
    log_level: str


@router.get("/v1/settings", response_model=SettingsResponse)
async def get_settings():
    """Get current configuration settings."""
    return SettingsResponse(
        ollama_url=settings.ollama_url,
        ollama_model=settings.ollama_model,
        read_roots=settings.read_roots_list,
        write_roots=settings.write_roots_list,
        sandbox_mode=settings.sandbox_mode,
        allow_network=settings.allow_network,
        log_level=settings.log_level,
    )


@router.post("/v1/settings")
async def update_settings(request: SettingsUpdateRequest):
    """Update configuration settings and save to .env file."""
    try:
        # Find the project root - where .env.example is located
        # This file is at: src/toolchat/api/routes_settings.py
        # Project root is 3 levels up from this file
        project_root = Path(__file__).parent.parent.parent.parent
        env_path = project_root / ".env"
        
        logger.info(f"Looking for .env file at: {env_path}")
        
        if not env_path.exists():
            # Create a new .env file if it doesn't exist
            logger.info(f".env file not found, creating new one at {env_path}")
            env_path.touch()
        
        # Read existing .env file
        env_lines = []
        if env_path.exists():
            with open(env_path, 'r') as f:
                env_lines = f.readlines()
        
        # Update settings
        updated_settings = {
            'OLLAMA_URL': request.ollama_url,
            'OLLAMA_MODEL': request.ollama_model,
            'READ_ROOTS': ','.join(request.read_roots),
            'WRITE_ROOTS': ','.join(request.write_roots),
            'SANDBOX_MODE': request.sandbox_mode,
            'ALLOW_NETWORK': str(request.allow_network).lower(),
            'LOG_LEVEL': request.log_level,
        }
        
        # Update or add settings in env_lines
        updated_keys = set()
        new_lines = []
        
        for line in env_lines:
            # Keep the original line ending
            line_stripped = line.rstrip('\n\r')
            if not line_stripped or line_stripped.startswith('#'):
                new_lines.append(line_stripped)
                continue
            
            if '=' in line_stripped:
                key = line_stripped.split('=', 1)[0].strip()
                if key in updated_settings:
                    new_lines.append(f"{key}={updated_settings[key]}")
                    updated_keys.add(key)
                else:
                    new_lines.append(line_stripped)
            else:
                new_lines.append(line_stripped)
        
        # Add any settings that weren't in the file
        for key, value in updated_settings.items():
            if key not in updated_keys:
                new_lines.append(f"{key}={value}")
        
        # Write back to .env file with proper newlines
        with open(env_path, 'w') as f:
            for line in new_lines:
                f.write(line + '\n')
        
        logger.info(f"Updated .env file at {env_path}")
        
        logger.info(f"Settings updated successfully")
        
        return {
            "message": "Settings updated successfully. Please restart the application for changes to take effect.",
            "restart_required": True
        }
    
    except Exception as e:
        logger.error(f"Failed to update settings: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to update settings: {str(e)}")
