import pytest
from pathlib import Path
from src.toolchat.infra.security import PathValidator, PathSecurityError


def test_path_validator_read_access():
    validator = PathValidator(
        read_roots=["/tmp/test"],
        write_roots=["/tmp/test/write"]
    )
    
    assert validator.can_read("/tmp/test/file.txt")
    assert not validator.can_read("/etc/passwd")
    assert not validator.can_read("/root/secret")


def test_path_validator_write_access():
    validator = PathValidator(
        read_roots=["/tmp/test"],
        write_roots=["/tmp/test/write"]
    )
    
    assert validator.can_write("/tmp/test/write/file.txt")
    assert not validator.can_write("/tmp/test/file.txt")
    assert not validator.can_write("/etc/config")


def test_path_validator_denied_paths():
    validator = PathValidator(
        read_roots=["/home/user"],
        write_roots=["/home/user/data"]
    )
    
    assert not validator.can_read("/etc/shadow")
    assert not validator.can_read("/boot/grub")
    assert not validator.can_write("/var/lib/data")


def test_path_normalization():
    validator = PathValidator(
        read_roots=["/tmp/test"],
        write_roots=["/tmp/test/write"]
    )
    
    normalized = validator.normalize_path("/tmp/test/../test/file.txt")
    assert "/.." not in str(normalized)


def test_validate_read_raises_on_denied():
    validator = PathValidator(
        read_roots=["/tmp/test"],
        write_roots=["/tmp/test/write"]
    )
    
    with pytest.raises(PathSecurityError):
        validator.validate_read("/etc/passwd")


def test_validate_write_raises_on_denied():
    validator = PathValidator(
        read_roots=["/tmp/test"],
        write_roots=["/tmp/test/write"]
    )
    
    with pytest.raises(PathSecurityError):
        validator.validate_write("/tmp/test/readonly.txt")
