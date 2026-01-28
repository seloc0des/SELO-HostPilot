import subprocess
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
from ..infra.logging import get_logger

logger = get_logger(__name__)


class ExifToolHelper:
    def __init__(self):
        self.exiftool_available = self._check_exiftool()
    
    def _check_exiftool(self) -> bool:
        try:
            result = subprocess.run(
                ["exiftool", "-ver"],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False
    
    def get_date_taken(self, image_path: Path) -> Optional[datetime]:
        if not self.exiftool_available:
            return None
        
        try:
            result = subprocess.run(
                ["exiftool", "-DateTimeOriginal", "-CreateDate", "-json", str(image_path)],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                return None
            
            data = json.loads(result.stdout)
            if not data:
                return None
            
            exif = data[0]
            
            for field in ["DateTimeOriginal", "CreateDate"]:
                if field in exif:
                    date_str = exif[field]
                    try:
                        return datetime.strptime(date_str, "%Y:%m:%d %H:%M:%S")
                    except ValueError:
                        try:
                            return datetime.strptime(date_str.split("+")[0].strip(), "%Y:%m:%d %H:%M:%S")
                        except ValueError:
                            continue
            
            return None
        
        except Exception as e:
            logger.warning(f"exiftool failed for {image_path}: {e}")
            return None
    
    def get_metadata(self, image_path: Path) -> Optional[Dict[str, Any]]:
        if not self.exiftool_available:
            return None
        
        try:
            result = subprocess.run(
                ["exiftool", "-json", str(image_path)],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                return None
            
            data = json.loads(result.stdout)
            return data[0] if data else None
        
        except Exception as e:
            logger.warning(f"exiftool metadata extraction failed for {image_path}: {e}")
            return None


exiftool_helper = ExifToolHelper()
