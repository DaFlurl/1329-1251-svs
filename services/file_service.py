# -*- coding: utf-8 -*-
"""
File Service for AgentDaf1.1
"""

import os
import hashlib
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional

class FileService:
    def __init__(self, base_dir: str = None):
        self.base_dir = Path(base_dir) if base_dir else Path.cwd()
        self.logger = logging.getLogger(__name__)
    
    def upload_file(self, file_data: bytes, filename: str, folder: str = "uploads") -> Dict[str, Any]:
        try:
            upload_dir = self.base_dir / folder
            upload_dir.mkdir(parents=True, exist_ok=True)
            
            file_path = upload_dir / filename
            counter = 1
            original_name = filename
            while file_path.exists():
                stem = Path(original_name).stem
                suffix = Path(original_name).suffix
                filename = f"{stem}_{counter}{suffix}"
                file_path = upload_dir / filename
                counter += 1
            
            with open(file_path, 'wb') as f:
                f.write(file_data)
            
            file_hash = hashlib.md5(file_data).hexdigest()
            
            file_info = {
                "filename": filename,
                "path": str(file_path),
                "size": len(file_data),
                "hash": file_hash
            }
            
            self.logger.info(f"File uploaded: {filename}")
            return {"success": True, "file_info": file_info}
            
        except Exception as e:
            self.logger.error(f"Upload failed: {e}")
            return {"success": False, "error": str(e)}
    
    def list_files(self, folder: str = "uploads") -> List[Dict[str, Any]]:
        try:
            folder_path = self.base_dir / folder
            if not folder_path.exists():
                return []
            
            files = []
            for file_path in folder_path.iterdir():
                if file_path.is_file():
                    stat = file_path.stat()
                    files.append({
                        "filename": file_path.name,
                        "size": stat.st_size,
                        "modified": stat.st_mtime
                    })
            
            return files
        except Exception as e:
            self.logger.error(f"List files failed: {e}")
            return []

file_service = FileService()
