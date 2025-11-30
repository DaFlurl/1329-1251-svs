#!/usr/bin/env python3
"""
Backup script for dataDeployed directory
"""
import shutil
from datetime import datetime
from pathlib import Path

def backup_data():
    source = Path("../dataDeployed")
    backup_dir = Path("backups")
    backup_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = backup_dir / f"data_backup_{timestamp}"
    
    if source.exists():
        shutil.copytree(source, backup_path)
        logger.info(f"Backup created: {backup_path}")
    else:
        logger.info("Source directory not found")

if __name__ == "__main__":
    backup_data()
