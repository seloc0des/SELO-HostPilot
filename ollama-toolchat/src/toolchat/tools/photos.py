import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Tuple
from PIL import Image
from PIL.ExifTags import TAGS
from .base import BaseTool, ToolSpec, ToolResult, ToolTier
from ..infra.security import path_validator
from ..infra.logging import get_logger
from .exiftool_helper import exiftool_helper

logger = get_logger(__name__)


class OrganizePhotosTool(BaseTool):
    def __init__(self):
        spec = ToolSpec(
            name="organize_photos",
            description="Organize photos into directories by date taken",
            args_schema={
                "type": "object",
                "properties": {
                    "input_dir": {
                        "type": "string",
                        "description": "Source directory containing photos"
                    },
                    "output_dir": {
                        "type": "string",
                        "description": "Destination directory for organized photos"
                    },
                    "mode": {
                        "type": "string",
                        "description": "Organization mode: 'yyyy_mm' or 'yyyy_mm_dd'",
                        "enum": ["yyyy_mm", "yyyy_mm_dd"],
                        "default": "yyyy_mm"
                    },
                    "dry_run": {
                        "type": "boolean",
                        "description": "If true, only show what would be done",
                        "default": True
                    }
                },
                "required": ["input_dir", "output_dir"]
            },
            tier=ToolTier.WRITE_SAFE,
            requires_confirmation=True,
            supports_dry_run=True,
        )
        super().__init__(spec)
    
    def _get_date_taken(self, image_path: Path) -> datetime:
        if exiftool_helper.exiftool_available:
            date_taken = exiftool_helper.get_date_taken(image_path)
            if date_taken:
                return date_taken
        
        try:
            image = Image.open(image_path)
            exif_data = image.getexif()
            
            if exif_data:
                for tag_id, value in exif_data.items():
                    tag = TAGS.get(tag_id, tag_id)
                    if tag == "DateTimeOriginal":
                        return datetime.strptime(value, "%Y:%m:%d %H:%M:%S")
            
            stat = image_path.stat()
            return datetime.fromtimestamp(stat.st_mtime)
        except Exception:
            stat = image_path.stat()
            return datetime.fromtimestamp(stat.st_mtime)
    
    def _get_target_dir(self, date_taken: datetime, mode: str, output_dir: Path) -> Path:
        if mode == "yyyy_mm":
            return output_dir / f"{date_taken.year}_{date_taken.month:02d}"
        else:
            return output_dir / f"{date_taken.year}_{date_taken.month:02d}_{date_taken.day:02d}"
    
    def _scan_photos(self, input_dir: Path) -> List[Tuple[Path, str]]:
        photo_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.heic', '.heif'}
        photos = []
        
        for item in input_dir.rglob('*'):
            if item.is_file() and item.suffix.lower() in photo_extensions:
                photos.append((item, item.suffix.lower()))
        
        return photos
    
    def execute(self, args: Dict[str, Any], dry_run: bool = False) -> ToolResult:
        input_dir_str = args.get("input_dir")
        output_dir_str = args.get("output_dir")
        mode = args.get("mode", "yyyy_mm")
        dry_run = args.get("dry_run", True) or dry_run
        
        try:
            input_dir = path_validator.validate_read(input_dir_str)
            output_dir = path_validator.validate_write(output_dir_str)
            
            if not input_dir.exists():
                return ToolResult(
                    ok=False,
                    error_code="input_not_found",
                    message=f"Input directory does not exist: {input_dir}"
                )
            
            photos = self._scan_photos(input_dir)
            
            if not photos:
                return ToolResult(
                    ok=True,
                    data={
                        "dry_run": dry_run,
                        "total_photos": 0,
                        "message": "No photos found in input directory"
                    }
                )
            
            plan = []
            for photo_path, ext in photos:
                date_taken = self._get_date_taken(photo_path)
                target_dir = self._get_target_dir(date_taken, mode, output_dir)
                target_path = target_dir / photo_path.name
                
                if target_path.exists() and target_path != photo_path:
                    base_name = photo_path.stem
                    suffix = photo_path.suffix
                    counter = 1
                    while target_path.exists():
                        target_path = target_dir / f"{base_name}_{counter}{suffix}"
                        counter += 1
                
                plan.append({
                    "source": str(photo_path),
                    "destination": str(target_path),
                    "date_taken": date_taken.isoformat(),
                })
            
            if not dry_run:
                for item in plan:
                    source = Path(item["source"])
                    dest = Path(item["destination"])
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    
                    if dest.exists() and dest != source:
                        base_name = dest.stem
                        suffix = dest.suffix
                        counter = 1
                        while dest.exists():
                            dest = dest.parent / f"{base_name}_{counter}{suffix}"
                            counter += 1
                    
                    shutil.move(str(source), str(dest))
                    logger.info(f"Moved {source} -> {dest}")
            
            return ToolResult(
                ok=True,
                data={
                    "dry_run": dry_run,
                    "total_photos": len(photos),
                    "plan": plan[:10],
                    "message": f"{'Would move' if dry_run else 'Moved'} {len(photos)} photos"
                }
            )
        except Exception as e:
            logger.error("organize_photos failed", exc_info=True)
            return ToolResult(
                ok=False,
                error_code="organize_photos_error",
                message=f"Failed to organize photos: {str(e)}"
            )
