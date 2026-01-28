import pytest
from pathlib import Path
from src.toolchat.tools.photos import OrganizePhotosTool
from src.toolchat.tools.base import ToolTier


def test_organize_photos_spec():
    tool = OrganizePhotosTool()
    
    assert tool.spec.name == "organize_photos"
    assert tool.spec.tier == ToolTier.WRITE_SAFE
    assert tool.spec.requires_confirmation is True
    assert tool.spec.supports_dry_run is True


def test_organize_photos_dry_run():
    tool = OrganizePhotosTool()
    
    args = {
        "input_dir": "/tmp/photos",
        "output_dir": "/tmp/organized",
        "mode": "yyyy_mm",
        "dry_run": True
    }
    
    result = tool.execute(args, dry_run=True)
    
    assert result is not None
    assert hasattr(result, 'ok')


def test_organize_photos_invalid_input():
    tool = OrganizePhotosTool()
    
    args = {
        "input_dir": "/nonexistent/path",
        "output_dir": "/tmp/organized",
        "mode": "yyyy_mm",
        "dry_run": True
    }
    
    result = tool.execute(args, dry_run=True)
    
    assert result.ok is False
