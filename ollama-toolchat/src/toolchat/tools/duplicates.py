"""Duplicate file finder tool using file hashes."""

import os
import hashlib
from pathlib import Path
from typing import Dict, Any, List
from collections import defaultdict
from .base import BaseTool, ToolSpec, ToolResult, ToolTier
from ..infra.security import path_validator
from ..infra.logging import get_logger

logger = get_logger(__name__)


class DuplicateFinderTool(BaseTool):
    def __init__(self):
        spec = ToolSpec(
            name="find_duplicates",
            description="Find duplicate files in a directory by comparing file hashes. Returns groups of files with identical content.",
            args_schema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Directory path to scan for duplicates"
                    },
                    "min_size_kb": {
                        "type": "integer",
                        "description": "Minimum file size in KB to consider (default: 1 KB, skips tiny files)",
                        "default": 1
                    },
                    "max_depth": {
                        "type": "integer",
                        "description": "Maximum directory depth to scan (default: 5)",
                        "default": 5
                    }
                },
                "required": ["path"]
            },
            tier=ToolTier.READ_ONLY,
            requires_confirmation=False,
            supports_dry_run=False,
            timeout_sec=120,
        )
        super().__init__(spec)
    
    def _get_file_hash(self, filepath: Path, quick: bool = True) -> str:
        """Compute MD5 hash of a file. If quick=True, only hash first 8KB for speed."""
        hasher = hashlib.md5()
        try:
            with open(filepath, 'rb') as f:
                if quick:
                    # Quick hash: first 8KB + file size
                    chunk = f.read(8192)
                    hasher.update(chunk)
                    hasher.update(str(filepath.stat().st_size).encode())
                else:
                    # Full hash
                    for chunk in iter(lambda: f.read(65536), b''):
                        hasher.update(chunk)
            return hasher.hexdigest()
        except (IOError, OSError) as e:
            logger.debug(f"Could not hash {filepath}: {e}")
            return ""
    
    def _format_size(self, size_bytes: int) -> str:
        """Format bytes as human-readable size."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.1f}{unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f}TB"
    
    def _scan_directory(self, base_path: Path, min_size: int, max_depth: int) -> Dict[int, List[Path]]:
        """Scan directory and group files by size (first pass filter)."""
        size_groups: Dict[int, List[Path]] = defaultdict(list)
        files_scanned = 0
        max_files = 10000  # Safety limit
        
        def scan_recursive(path: Path, depth: int):
            nonlocal files_scanned
            if depth > max_depth or files_scanned >= max_files:
                return
            
            try:
                for entry in os.scandir(path):
                    if files_scanned >= max_files:
                        break
                    
                    try:
                        if entry.is_file(follow_symlinks=False):
                            size = entry.stat().st_size
                            if size >= min_size:
                                size_groups[size].append(Path(entry.path))
                                files_scanned += 1
                        elif entry.is_dir(follow_symlinks=False):
                            # Skip common non-content directories
                            if entry.name not in ['.git', 'node_modules', '__pycache__', '.venv', 'venv', '.cache']:
                                scan_recursive(Path(entry.path), depth + 1)
                    except (PermissionError, OSError):
                        continue
            except (PermissionError, OSError):
                pass
        
        scan_recursive(base_path, 0)
        return size_groups, files_scanned
    
    def execute(self, args: Dict[str, Any], dry_run: bool = False) -> ToolResult:
        path = args.get("path")
        min_size_kb = args.get("min_size_kb", 1)
        max_depth = args.get("max_depth", 5)
        
        if not path:
            return ToolResult(
                ok=False,
                error_code="missing_path",
                message="Path is required"
            )
        
        # Validate depth
        if max_depth < 1 or max_depth > 10:
            return ToolResult(
                ok=False,
                error_code="invalid_depth",
                message="max_depth must be between 1 and 10"
            )
        
        try:
            # Validate path access
            validated_path = path_validator.validate_read(path)
            base_path = Path(validated_path)
            
            if not base_path.is_dir():
                return ToolResult(
                    ok=False,
                    error_code="not_a_directory",
                    message=f"'{path}' is not a directory"
                )
            
            min_size_bytes = min_size_kb * 1024
            
            # First pass: group files by size
            size_groups, files_scanned = self._scan_directory(base_path, min_size_bytes, max_depth)
            
            # Second pass: hash files that have size duplicates
            duplicates: List[Dict[str, Any]] = []
            total_wasted_space = 0
            
            for size, files in size_groups.items():
                if len(files) < 2:
                    continue
                
                # Group by hash
                hash_groups: Dict[str, List[Path]] = defaultdict(list)
                for filepath in files:
                    file_hash = self._get_file_hash(filepath, quick=True)
                    if file_hash:
                        hash_groups[file_hash].append(filepath)
                
                # Find actual duplicates (same hash = same content)
                for file_hash, dup_files in hash_groups.items():
                    if len(dup_files) >= 2:
                        # Verify with full hash for files that matched quick hash
                        if size > 8192:  # Only verify if file is larger than quick hash size
                            full_hash_groups: Dict[str, List[Path]] = defaultdict(list)
                            for f in dup_files:
                                full_hash = self._get_file_hash(f, quick=False)
                                if full_hash:
                                    full_hash_groups[full_hash].append(f)
                            
                            for fh, verified_dups in full_hash_groups.items():
                                if len(verified_dups) >= 2:
                                    wasted = size * (len(verified_dups) - 1)
                                    total_wasted_space += wasted
                                    duplicates.append({
                                        "size": self._format_size(size),
                                        "size_bytes": size,
                                        "count": len(verified_dups),
                                        "wasted_space": self._format_size(wasted),
                                        "files": [str(f) for f in verified_dups[:5]]  # Limit to 5 paths
                                    })
                        else:
                            wasted = size * (len(dup_files) - 1)
                            total_wasted_space += wasted
                            duplicates.append({
                                "size": self._format_size(size),
                                "size_bytes": size,
                                "count": len(dup_files),
                                "wasted_space": self._format_size(wasted),
                                "files": [str(f) for f in dup_files[:5]]
                            })
            
            # Sort by wasted space (largest first)
            duplicates.sort(key=lambda x: x["size_bytes"] * x["count"], reverse=True)
            
            # Limit results
            top_duplicates = duplicates[:20]
            
            return ToolResult(
                ok=True,
                data={
                    "scanned_path": str(base_path),
                    "files_scanned": files_scanned,
                    "duplicate_groups": len(duplicates),
                    "total_duplicate_files": sum(d["count"] for d in duplicates),
                    "total_wasted_space": self._format_size(total_wasted_space),
                    "top_duplicates": top_duplicates
                }
            )
            
        except Exception as e:
            logger.error(f"find_duplicates failed for {path}", exc_info=True)
            return ToolResult(
                ok=False,
                error_code="duplicate_finder_error",
                message=f"Failed to find duplicates: {str(e)}"
            )
