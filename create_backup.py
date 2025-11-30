#!/usr/bin/env python3
"""
AgentDaf1.1 Space-Efficient Backup Creator
Creates compressed backups with minimal space usage
"""

import os
import json
import zipfile
import gzip
import shutil
import tarfile
import subprocess
from pathlib import Path
from datetime import datetime
import sys

class SpaceEfficientBackup:
    def __init__(self, base_dir):
        self.base_dir = Path(base_dir)
        self.backup_dir = self.base_dir / "backups"
        self.backup_dir.mkdir(exist_ok=True)
        
    def get_directory_size(self, path):
        """Calculate total size of directory"""
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(path):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                if os.path.exists(filepath):
                    total_size += os.path.getsize(filepath)
        return total_size
    
    def analyze_project_structure(self):
        """Analyze project to determine optimal backup strategy"""
        logger.info("🔍 Analyzing project structure...")
        
        analysis = {
            'total_size': 0,
            'directories': {},
            'large_files': [],
            'compressible_files': [],
            'binary_files': [],
            'cache_dirs': [],
            'temp_dirs': []
        }
        
        # Analyze main directories
        for item in self.base_dir.iterdir():
            if item.name == 'backups':
                continue
                
            if item.is_dir():
                size = self.get_directory_size(item)
                analysis['directories'][item.name] = size
                analysis['total_size'] += size
                
                # Identify special directories
                if item.name in ['__pycache__', '.git', 'node_modules', '.pytest_cache']:
                    analysis['cache_dirs'].append(item.name)
                elif item.name in ['temp', 'tmp', '.tmp']:
                    analysis['temp_dirs'].append(item.name)
                    
            elif item.is_file():
                size = item.stat().st_size
                analysis['total_size'] += size
                
                # Categorize files
                if size > 10 * 1024 * 1024:  # > 10MB
                    analysis['large_files'].append((item.name, size))
                
                # Check file type for compressibility
                ext = item.suffix.lower()
                if ext in ['.txt', '.py', '.js', '.html', '.css', '.json', '.md', '.csv']:
                    analysis['compressible_files'].append(item.name)
                elif ext in ['.zip', '.gz', '.tar', '.bz2', '.7z', '.jpg', '.png', '.gif', '.mp4', '.exe']:
                    analysis['binary_files'].append(item.name)
        
        return analysis
    
    def create_minimal_backup(self):
        """Create most space-efficient backup"""
        logger.info("🗜️  Creating minimal space-efficient backup...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"minimal_backup_{timestamp}"
        
        # Create temporary directory for minimal backup
        temp_dir = self.backup_dir / f"temp_{backup_name}"
        temp_dir.mkdir(exist_ok=True)
        
        try:
            # Copy essential files only
            essential_files = [
                'README.md',
                'requirements.txt',
                'package.json',
                'config.json',
                '.gitignore',
                'docker-compose.yml',
                'Dockerfile'
            ]
            
            # Copy essential files
            for file in essential_files:
                src = self.base_dir / file
                if src.exists():
                    dst = temp_dir / file
                    shutil.copy2(src, dst)
                    logger.info(f"✓ Copied essential: {file}")
            
            # Copy important directories (excluding caches)
            important_dirs = [
                'src',
                'gitsitestylewebseite',
                'config',
                'services',
                'enterprise'
            ]
            
            for dir_name in important_dirs:
                src_dir = self.base_dir / dir_name
                if src_dir.exists():
                    dst_dir = temp_dir / dir_name
                    self.copy_directory_minimal(src_dir, dst_dir)
                    logger.info(f"✓ Copied directory: {dir_name}")
            
            # Create backup archive with maximum compression
            archive_path = self.backup_dir / f"{backup_name}.tar.gz"
            self.create_compressed_archive(temp_dir, archive_path)
            
            # Get final size
            final_size = archive_path.stat().st_size
            original_size = self.get_directory_size(self.base_dir)
            compression_ratio = (1 - final_size / original_size) * 100
            
            logger.info(f"/n📊 Backup Statistics:")
            logger.info(f"   Original size: {self.format_size(original_size)}")
            logger.info(f"   Backup size: {self.format_size(final_size)}")
            logger.info(f"   Space saved: {compression_ratio:.1f}%")
            logger.info(f"   Location: {archive_path}")
            
            return archive_path
            
        finally:
            # Clean up temp directory
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
    
    def copy_directory_minimal(self, src_dir, dst_dir):
        """Copy directory excluding unnecessary files"""
        dst_dir.mkdir(parents=True, exist_ok=True)
        
        exclude_patterns = [
            '__pycache__',
            '.git',
            'node_modules',
            '.pytest_cache',
            '.vscode',
            '.idea',
            '*.pyc',
            '*.pyo',
            '*.log',
            '.DS_Store',
            'Thumbs.db',
            '*.tmp',
            '*.temp'
        ]
        
        for item in src_dir.iterdir():
            # Skip excluded patterns
            if any(pattern.replace('*', '') in item.name for pattern in exclude_patterns):
                continue
            
            if item.is_dir():
                self.copy_directory_minimal(item, dst_dir / item.name)
            else:
                # Skip large binary files that aren't essential
                if item.suffix.lower() in ['.exe', '.dll', '.so', '.dylib']:
                    continue
                
                dst = dst_dir / item.name
                shutil.copy2(item, dst)
    
    def create_compressed_archive(self, source_dir, output_path):
        """Create highly compressed archive"""
        logger.info("🗜️  Creating maximum compression archive...")
        
        # Use tar with gzip for maximum compression
        with tarfile.open(output_path, 'w:gz', compresslevel=9) as tar:
            tar.add(source_dir, arcname=output_path.stem)
    
    def create_7z_backup(self):
        """Create 7z backup (best compression)"""
        logger.info("📦 Creating 7z backup (best compression)...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"7z_backup_{timestamp}"
        archive_path = self.backup_dir / f"{backup_name}.7z"
        
        # Create file list for 7z
        temp_list = self.backup_dir / "backup_list.txt"
        with open(temp_list, 'w') as f:
            for item in self.base_dir.iterdir():
                if item.name != 'backups' and not item.name.startswith('.'):
                    f.write(f"{item}/n")
        
        try:
            # Try to use 7z if available
            try:
                cmd = [
                    '7z', 'a', '-t7z', '-mx=9', '-m0=lzma2',
                    str(archive_path), f'@{temp_list}'
                ]
                subprocess.run(cmd, cwd=self.base_dir, check=True, capture_output=True)
                
                size = archive_path.stat().st_size
                logger.info(f"✓ 7z backup created: {self.format_size(size)}")
                return archive_path
                
            except (subprocess.CalledProcessError, FileNotFoundError):
                logger.info("⚠️ 7z not available, using tar.gz instead")
                return self.create_minimal_backup()
                
        finally:
            if temp_list.exists():
                temp_list.unlink()
    
    def create_differential_backup(self):
        """Create differential backup (only changed files)"""
        logger.info("🔄 Creating differential backup...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"differential_backup_{timestamp}"
        
        # Find most recent full backup
        full_backups = list(self.backup_dir.glob("minimal_backup_*.tar.gz"))
        if not full_backups:
            logger.info("⚠️ No full backup found, creating full backup instead")
            return self.create_minimal_backup()
        
        latest_backup = max(full_backups, key=lambda x: x.stat().st_mtime)
        
        # This is a simplified differential backup
        # In production, you'd track file changes more carefully
        temp_dir = self.backup_dir / f"temp_{backup_name}"
        temp_dir.mkdir(exist_ok=True)
        
        try:
            # Copy recently modified files (last 24 hours)
            cutoff_time = datetime.now().timestamp() - 24 * 3600
            
            for item in self.base_dir.iterdir():
                if item.name == 'backups':
                    continue
                    
                if item.stat().st_mtime > cutoff_time:
                    if item.is_file():
                        shutil.copy2(item, temp_dir / item.name)
                    elif item.is_dir():
                        shutil.copytree(item, temp_dir / item.name, dirs_exist_ok=True)
            
            # Create archive
            archive_path = self.backup_dir / f"{backup_name}.tar.gz"
            self.create_compressed_archive(temp_dir, archive_path)
            
            size = archive_path.stat().st_size
            logger.info(f"✓ Differential backup created: {self.format_size(size)}")
            return archive_path
            
        finally:
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
    
    def format_size(self, size_bytes):
        """Format file size in human readable format"""
        if size_bytes == 0:
            return "0B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f}{size_names[i]}"
    
    def cleanup_old_backups(self, keep_count=5):
        """Remove old backups, keeping only the most recent"""
        logger.info(f"🧹 Cleaning up old backups (keeping {keep_count})...")
        
        # Get all backup files
        backup_files = list(self.backup_dir.glob("*.tar.gz")) + list(self.backup_dir.glob("*.7z"))
        
        if len(backup_files) <= keep_count:
            logger.info("✓ No cleanup needed")
            return
        
        # Sort by modification time (newest first)
        backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        # Remove old backups
        for backup_file in backup_files[keep_count:]:
            backup_file.unlink()
            logger.info(f"🗑️  Removed: {backup_file.name}")
        
        logger.info(f"✓ Cleanup complete, kept {keep_count} most recent backups")
    
    def show_backup_menu(self):
        """Show backup options menu"""
        analysis = self.analyze_project_structure()
        
        logger.info("/n" + "="*60)
        logger.info("📦 AGENTDAF1.1 BACKUP CREATOR")
        logger.info("="*60)
        
        logger.info(f"/n📊 Project Analysis:")
        logger.info(f"   Total size: {self.format_size(analysis['total_size'])}")
        logger.info(f"   Directories: {len(analysis['directories'])}")
        logger.info(f"   Large files: {len(analysis['large_files'])}")
        logger.info(f"   Cache directories: {len(analysis['cache_dirs'])}")
        
        if analysis['cache_dirs']:
            logger.info(f"   Cache dirs to exclude: {', '.join(analysis['cache_dirs'])}")
        
        logger.info(f"/n🎯 Backup Options (Space-Efficient):")
        logger.info(f"   1. Minimal Backup (tar.gz, high compression)")
        logger.info(f"   2. 7z Backup (best compression, smallest size)")
        logger.info(f"   3. Differential Backup (only recent changes)")
        logger.info(f"   4. All formats (for comparison)")
        logger.info(f"   5. Cleanup old backups")
        logger.info(f"   0. Exit")
        
        while True:
            try:
                choice = input(f"/nSelect option (0-5): ").strip()
                
                if choice == '0':
                    logger.info("👋 Backup creator exited")
                    break
                elif choice == '1':
                    self.create_minimal_backup()
                elif choice == '2':
                    self.create_7z_backup()
                elif choice == '3':
                    self.create_differential_backup()
                elif choice == '4':
                    logger.info("🔄 Creating all backup formats...")
                    self.create_minimal_backup()
                    self.create_7z_backup()
                    self.create_differential_backup()
                elif choice == '5':
                    keep = input("How many backups to keep? (default 5): ").strip()
                    keep_count = int(keep) if keep.isdigit() else 5
                    self.cleanup_old_backups(keep_count)
                else:
                    logger.info("❌ Invalid option, please try again")
                    
            except KeyboardInterrupt:
                logger.info("/n👋 Backup creator interrupted")
                break
            except Exception as e:
                logger.info(f"❌ Error: {e}")

def main():
    if len(sys.argv) > 1:
        base_dir = sys.argv[1]
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
    
    backup_creator = SpaceEfficientBackup(base_dir)
    backup_creator.show_backup_menu()

if __name__ == "__main__":
    main()