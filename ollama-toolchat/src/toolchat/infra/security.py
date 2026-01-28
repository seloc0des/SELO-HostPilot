from pathlib import Path
from typing import List, Optional
from ..config import settings
from .logging import get_logger

logger = get_logger(__name__)


class PathSecurityError(Exception):
    pass


class PathValidator:
    def __init__(self, read_roots: List[str], write_roots: List[str]):
        self.read_roots = [Path(r).resolve() for r in read_roots]
        self.write_roots = [Path(w).resolve() for w in write_roots]
        
        self.denied_paths = [
            Path("/etc"),
            Path("/boot"),
            Path("/root"),
            Path("/var/lib"),
            Path("/usr"),
            Path.home() / ".ssh",
        ]
    
    def normalize_path(self, path: str) -> Path:
        try:
            p = Path(path).expanduser()
            if p.exists():
                p = p.resolve()
            else:
                p = p.resolve(strict=False)
            return p
        except Exception as e:
            raise PathSecurityError(f"Invalid path: {path}") from e
    
    def is_denied(self, path: Path) -> bool:
        for denied in self.denied_paths:
            try:
                path.relative_to(denied)
                return True
            except ValueError:
                continue
        return False
    
    def can_read(self, path: str) -> bool:
        try:
            normalized = self.normalize_path(path)
            
            if self.is_denied(normalized):
                logger.warning(f"Denied read access to: {normalized}")
                return False
            
            for root in self.read_roots:
                try:
                    normalized.relative_to(root)
                    return True
                except ValueError:
                    continue
            
            logger.warning(f"Path not in read roots: {normalized}")
            return False
        except PathSecurityError:
            return False
    
    def can_write(self, path: str) -> bool:
        try:
            normalized = self.normalize_path(path)
            
            if self.is_denied(normalized):
                logger.warning(f"Denied write access to: {normalized}")
                return False
            
            for root in self.write_roots:
                try:
                    normalized.relative_to(root)
                    return True
                except ValueError:
                    continue
            
            logger.warning(f"Path not in write roots: {normalized}")
            return False
        except PathSecurityError:
            return False
    
    def validate_read(self, path: str) -> Path:
        if not self.can_read(path):
            raise PathSecurityError(f"Read access denied: {path}")
        return self.normalize_path(path)
    
    def validate_write(self, path: str) -> Path:
        if not self.can_write(path):
            raise PathSecurityError(f"Write access denied: {path}")
        return self.normalize_path(path)


path_validator = PathValidator(
    read_roots=settings.read_roots_list,
    write_roots=settings.write_roots_list
)
