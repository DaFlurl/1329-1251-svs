#!/usr/bin/env python3
"""
Project Restructuring Script for AgentDaf1.1
Automatically organizes files into a clean, logical folder structure
"""

import os
import shutil
import json
from pathlib import Path
from typing import Dict, List, Set
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ProjectRestructurer:
    def __init__(self, base_dir: str = None):
        self.base_dir = Path(base_dir) if base_dir else Path.cwd()
        self.moved_files = []
        self.created_dirs = []
        self.errors = []
        
        # Define folder structure and file mappings
        self.folder_structure = {
            # Core application code
            'src': {
                'extensions': ['.py', '.js', '.ts', '.html', '.css', '.jsx', '.tsx', '.vue', '.php', '.java', '.cpp', '.c', '.h'],
                'subfolders': {
                    'api': ['flask_api.py', 'enhanced_flask_api.py', 'github_integration.py'],
                    'core': ['excel_processor.py', 'dashboard_generator.py'],
                    'config': ['settings.py', 'logging.py'],
                    'tools': ['neural_memory.py', 'ai_tools.py', 'docker_mcp_tools.py', 'memory_manager.py', 'task_manager.py'],
                    'web': ['templates', 'static'],
                    'main': ['main.py', 'app.py']
                }
            },
            
            # Assets and media
            'assets': {
                'subfolders': {
                    'images': ['.png', '.jpg', '.jpeg', '.svg', '.gif', '.bmp', '.ico', '.webp'],
                    'sounds': ['.mp3', '.wav', '.ogg', '.flac', '.aac'],
                    'videos': ['.mp4', '.avi', '.mov', '.wmv', '.flv'],
                    'fonts': ['.ttf', '.otf', '.woff', '.woff2', '.eot'],
                    'data': ['.json', '.xml', '.csv', '.xlsx', '.xls', '.sqlite', '.db']
                }
            },
            
            # Documentation
            'docs': {
                'extensions': ['.md', '.txt', '.pdf', '.docx', '.doc', '.rst'],
                'subfolders': {
                    'manuals': ['README.md', 'ANLEITUNG.md', 'MANUAL.md'],
                    'api': ['API.md', 'api_docs'],
                    'architecture': ['ARCHITECTURE.md', 'DESIGN.md'],
                    'deployment': ['DEPLOYMENT.md', 'INSTALL.md']
                }
            },
            
            # Tests
            'tests': {
                'extensions': ['.spec.js', '.test.js', '.spec.ts', '.test.ts', '.test.py'],
                'subfolders': {
                    'unit': ['test_*.py', '*_test.py'],
                    'integration': ['integration_test*.py'],
                    'e2e': ['e2e_test*.py']
                }
            },
            
            # Build and distribution
            'build': {
                'extensions': ['.exe', '.zip', '.tar.gz', '.dist', '.deb', '.rpm', '.dmg'],
                'subfolders': {
                    'release': ['release.*', 'final.*'],
                    'artifacts': ['*.artifact', 'build_output']
                }
            },
            
            # Configuration files
            'config': {
                'extensions': ['.env', '.yml', '.yaml', '.toml', '.ini', '.conf', '.config'],
                'subfolders': {
                    'docker': ['docker-compose*.yml', 'Dockerfile*'],
                    'nginx': ['nginx*.conf'],
                    'systemd': ['*.service']
                }
            },
            
            # Scripts and automation
            'scripts': {
                'extensions': ['.sh', '.bat', '.ps1'],
                'subfolders': {
                    'deployment': ['deploy*', 'start*', 'finish*'],
                    'maintenance': ['backup*', 'repair*', 'fix*', 'health*'],
                    'development': ['dev*', 'debug*', 'test*']
                }
            },
            
            # Data and databases
            'data': {
                'subfolders': {
                    'databases': ['*.db', '*.sqlite'],
                    'backups': ['backup*', '*.bak'],
                    'processed': ['processed*', '*.processed'],
                    'raw': ['raw*', '*.raw'],
                    'cache': ['cache*', 'tmp*']
                }
            },
            
            # Enterprise components
            'enterprise': {
                'subfolders': {
                    'services': ['auth-service', 'api-gateway', 'analytics-service'],
                    'infrastructure': ['monitoring', 'nginx', 'rabbitmq'],
                    'database': ['migrations', 'schemas'],
                    'gateway': ['main.py', 'config'],
                    'web': ['frontend', 'backend']
                }
            },
            
            # Docker components
            'docker': {
                'subfolders': {
                    'configs': ['*.conf', 'config*'],
                    'scripts': ['*.sh', 'startup*'],
                    'src': ['main.py', 'performance_monitor.py'],
                    'docker_files': ['Dockerfile*', 'docker-compose*']
                }
            },
            
            # Tools and utilities
            'tools': {
                'extensions': ['.py'],
                'subfolders': {
                    'system': ['health_monitor.py', 'dependency_manager.py', 'auto_repair.py'],
                    'management': ['mcp_manager.py', 'secrets_manager.py', 'tools_launcher.py'],
                    'security': ['security_audit.py']
                }
            },
            
            # Services
            'services': {
                'subfolders': {
                    'microservices': ['*-service'],
                    'websocket': ['websocket_service.py'],
                    'api': ['api-*'],
                    'background': ['worker*', 'scheduler*']
                }
            },
            
            # Temporary and cache files
            'temp': {
                'subfolders': {
                    'cache': ['__pycache__', '*.pyc', '.pytest_cache'],
                    'logs': ['*.log', 'logs'],
                    'tmp': ['tmp*', 'temp*']
                }
            }
        }
        
        # Files to keep in root
        self.root_files = {
            '.gitignore', '.git', 'LICENSE', 'package.json', 'requirements.txt', 
            'pyproject.toml', 'setup.py', 'Makefile', 'CHANGELOG.md'
        }
        
        # Special file mappings
        self.special_mappings = {
            'docker-compose.yml': 'config/docker/',
            'docker-compose.enterprise.yml': 'config/docker/',
            'docker-compose.messaging.yml': 'config/docker/',
            'Dockerfile': 'config/docker/',
            'nginx.conf': 'config/nginx/',
            'nginx-production.conf': 'config/nginx/',
            'agentdaf1.service': 'config/systemd/',
            'gunicorn.conf.py': 'config/',
            '.env.example': 'config/',
            '.env.merged': 'config/',
            'tsconfig.json': 'config/',
            'requirements.txt': 'config/',
            'requirements-production.txt': 'config/',
            'requirements-integration.txt': 'config/'
        }

    def create_directory_structure(self):
        """Create the complete directory structure"""
        logger.info("Creating directory structure...")
        
        for folder_name, folder_config in self.folder_structure.items():
            folder_path = self.base_dir / folder_name
            
            if not folder_path.exists():
                folder_path.mkdir(parents=True, exist_ok=True)
                self.created_dirs.append(str(folder_path))
                logger.info(f"Created directory: {folder_path}")
            
            # Create subfolders
            if 'subfolders' in folder_config:
                for subfolder in folder_config['subfolders'].keys():
                    subfolder_path = folder_path / subfolder
                    if not subfolder_path.exists():
                        subfolder_path.mkdir(parents=True, exist_ok=True)
                        self.created_dirs.append(str(subfolder_path))
                        logger.info(f"Created subdirectory: {subfolder_path}")

    def get_target_folder(self, file_path: Path) -> Path:
        """Determine the target folder for a given file"""
        file_name = file_path.name
        file_ext = file_path.suffix.lower()
        
        # Check special mappings first
        if file_name in self.special_mappings:
            return self.base_dir / self.special_mappings[file_name]
        
        # Check if it's a root file
        if file_name in self.root_files or file_name.startswith('.git'):
            return self.base_dir
        
        # Check folder mappings
        for folder_name, folder_config in self.folder_structure.items():
            # Check by extension
            if 'extensions' in folder_config and file_ext in folder_config['extensions']:
                return self.base_dir / folder_name
            
            # Check by subfolder patterns
            if 'subfolders' in folder_config:
                for subfolder_name, patterns in folder_config['subfolders'].items():
                    if isinstance(patterns, list):
                        for pattern in patterns:
                            if self._matches_pattern(file_name, pattern):
                                return self.base_dir / folder_name / subfolder_name
        
        # Default to src for code files
        if file_ext in ['.py', '.js', '.ts', '.html', '.css']:
            return self.base_dir / 'src'
        
        # Default to docs for documentation
        if file_ext in ['.md', '.txt', '.pdf']:
            return self.base_dir / 'docs'
        
        # Default to config for configuration
        if file_ext in ['.json', '.yml', '.yaml', '.env', '.conf']:
            return self.base_dir / 'config'
        
        # Default to data for data files
        if file_ext in ['.xlsx', '.csv', '.db', '.sqlite']:
            return self.base_dir / 'data'
        
        # If no match, keep in root
        return self.base_dir

    def _matches_pattern(self, filename: str, pattern: str) -> bool:
        """Check if filename matches a pattern"""
        if '*' in pattern:
            import fnmatch
            return fnmatch.fnmatch(filename, pattern)
        return filename == pattern or filename.startswith(pattern.replace('*', ''))

    def move_files(self):
        """Move files to their appropriate folders"""
        logger.info("Moving files to appropriate folders...")
        
        # Get all files in current directory and subdirectories
        for file_path in self.base_dir.rglob('*'):
            if file_path.is_file() and file_path.parent == self.base_dir:
                # Skip if it's one of our script files
                if file_path.name in ['restructure_project.py', 'cleanup.js']:
                    continue
                
                target_folder = self.get_target_folder(file_path)
                
                if target_folder != self.base_dir and target_folder != file_path.parent:
                    target_path = target_folder / file_path.name
                    
                    # Handle name conflicts
                    counter = 1
                    original_target = target_path
                    while target_path.exists():
                        stem = original_target.stem
                        suffix = original_target.suffix
                        target_path = target_folder / f"{stem}_{counter}{suffix}"
                        counter += 1
                    
                    try:
                        shutil.move(str(file_path), str(target_path))
                        self.moved_files.append((str(file_path), str(target_path)))
                        logger.info(f"Moved: {file_path.name} → {target_folder.relative_to(self.base_dir)}")
                    except Exception as e:
                        self.errors.append(f"Failed to move {file_path}: {e}")
                        logger.error(f"Failed to move {file_path}: {e}")

    def clean_empty_directories(self):
        """Remove empty directories"""
        logger.info("Removing empty directories...")
        
        for root, dirs, files in os.walk(self.base_dir, topdown=False):
            for dir_name in dirs:
                dir_path = Path(root) / dir_name
                try:
                    if not any(dir_path.iterdir()):  # Directory is empty
                        dir_path.rmdir()
                        logger.info(f"Removed empty directory: {dir_path}")
                except OSError:
                    # Directory not empty or other error
                    pass

    def generate_report(self):
        """Generate a report of the restructuring process"""
        report = {
            'timestamp': str(Path.ctime(Path.now()) if hasattr(Path.now(), 'ctime') else '2025-11-27'),
            'base_directory': str(self.base_dir),
            'created_directories': self.created_dirs,
            'moved_files': self.moved_files,
            'errors': self.errors,
            'summary': {
                'directories_created': len(self.created_dirs),
                'files_moved': len(self.moved_files),
                'errors': len(self.errors)
            }
        }
        
        # Save report
        report_path = self.base_dir / 'docs' / 'restructure_report.json'
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        # Print summary
        logger.info("/n" + "="*60)
        logger.info("PROJECT RESTRUCTURING COMPLETE")
        logger.info("="*60)
        logger.info(f"Base Directory: {self.base_dir}")
        logger.info(f"Directories Created: {len(self.created_dirs)}")
        logger.info(f"Files Moved: {len(self.moved_files)}")
        logger.info(f"Errors: {len(self.errors)}")
        
        if self.errors:
            logger.info("/nErrors:")
            for error in self.errors:
                logger.info(f"  - {error}")
        
        logger.info(f"/nDetailed report saved to: {report_path}")
        
        # Show new structure
        self.show_directory_structure()

    def show_directory_structure(self, max_depth=3):
        """Display the directory structure"""
        logger.info("/n" + "="*60)
        logger.info("NEW DIRECTORY STRUCTURE")
        logger.info("="*60)
        
        def print_tree(path, prefix="", max_depth=3, current_depth=0):
            if current_depth >= max_depth:
                return
            
            items = sorted([item for item in path.iterdir() if not item.name.startswith('.')])
            for i, item in enumerate(items):
                is_last = i == len(items) - 1
                current_prefix = "└── " if is_last else "├── "
                logger.info(f"{prefix}{current_prefix}{item.name}")
                
                if item.is_dir() and current_depth < max_depth - 1:
                    next_prefix = prefix + ("    " if is_last else "│   ")
                    print_tree(item, next_prefix, max_depth, current_depth + 1)
        
        print_tree(self.base_dir, max_depth=max_depth)

    def run_restructure(self):
        """Run the complete restructuring process"""
        logger.info("Starting project restructuring...")
        
        try:
            self.create_directory_structure()
            self.move_files()
            self.clean_empty_directories()
            self.generate_report()
            
            logger.info("Project restructuring completed successfully!")
            
        except Exception as e:
            logger.error(f"Restructuring failed: {e}")
            raise

def main():
    """Main function"""
    logger.info("AgentDaf1.1 Project Restructuring Tool")
    logger.info("="*50)
    
    # Get base directory
    base_dir = input("Enter base directory (press Enter for current): ").strip()
    if not base_dir:
        base_dir = Path.cwd()
    
    # Confirm
    logger.info(f"/nRestructuring project in: {base_dir}")
    confirm = input("This will move and reorganize files. Continue? (y/N): ").strip().lower()
    
    if confirm != 'y':
        logger.info("Operation cancelled.")
        return
    
    # Run restructuring
    restructurer = ProjectRestructurer(base_dir)
    restructurer.run_restructure()

if __name__ == "__main__":
    main()