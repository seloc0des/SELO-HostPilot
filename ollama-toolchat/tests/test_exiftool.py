import pytest
from pathlib import Path
from src.toolchat.tools.exiftool_helper import ExifToolHelper


def test_exiftool_helper_init():
    helper = ExifToolHelper()
    assert isinstance(helper.exiftool_available, bool)


def test_exiftool_check():
    helper = ExifToolHelper()
    available = helper._check_exiftool()
    assert isinstance(available, bool)


def test_get_date_taken_no_file():
    helper = ExifToolHelper()
    result = helper.get_date_taken(Path("/nonexistent/file.jpg"))
    
    if helper.exiftool_available:
        assert result is None
    else:
        assert result is None


def test_get_metadata_no_file():
    helper = ExifToolHelper()
    result = helper.get_metadata(Path("/nonexistent/file.jpg"))
    
    assert result is None
