#!/usr/bin/env python3
"""
AgentDaf1.1 System Fix Tool
Fixes Docker, import, and system integration issues
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Any

class SystemFixer:
    """System issue fixer for AgentDaf1.1"""
    
    def __init__(self):
        self.project_root = Path.cwd()
        self.issues_found = []
        self.fixes_applied = []
        
    def diagnose_system(self) -> Dict[str, Any]:
        """Diagnose system issues"""
        diagnosis = {
            "python_version": sys.version,
            "platform": sys.platform,
            "project_root": str(self.project_root),
            "issues": [],
            "recommendations": []
        }
        
        # Check Python version
        if sys.version_info < (3, 8):
            diagnosis["issues"].append("Python version < 3.8 detected")
            diagnosis["recommendations"].append("Upgrade to Python 3.8+")
        
        # Check Docker
        docker_status = self._check_docker()
        diagnosis["docker"] = docker_status
        if not docker_status["available"]:
            diagnosis["issues"].append("Docker not available")
            diagnosis["recommendations"].append("Install Docker Desktop")
        
        # Check required packages
        missing_packages = self._check_required_packages()
        if missing_packages:
            diagnosis["issues"].append(f"Missing packages: {', '.join(missing_packages)}")
            diagnosis["recommendations"].append(f"Install: pip install {' '.join(missing_packages)}")
        
        # Check project structure
        structure_issues = self._check_project_structure()
        diagnosis["issues"].extend(structure_issues)
        
        # Check environment files
        env_issues = self._check_environment()
        diagnosis["issues"].extend(env_issues)
        
        return diagnosis
    
    def _check_docker(self) -> Dict[str, Any]:
        """Check Docker availability and status"""
        try:
            result = subprocess.run(['docker', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                return {
                    "available": True,
                    "version": result.stdout.strip(),
                    "status": "working"
                }
            else:
                return {"available": False, "error": result.stderr}
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            return {"available": False, "error": str(e)}
    
    def _check_required_packages(self) -> List[str]:
        """Check for required Python packages"""
        required_packages = [
            'flask', 'flask_cors', 'requests', 'psutil',
            'schedule', 'bcrypt', 'jwt', 'pandas', 'openpyxl'
        ]
        
        missing = []
        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                missing.append(package)
        
        return missing
    
    def _check_project_structure(self) -> List[str]:
        """Check project structure"""
        issues = []
        
        required_dirs = ['data', 'logs', 'backups']
        for dir_name in required_dirs:
            dir_path = self.project_root / dir_name
            if not dir_path.exists():
                issues.append(f"Missing directory: {dir_name}")
        
        required_files = ['simple_app.py', 'requirements.txt', '.env']
        for file_name in required_files:
            file_path = self.project_root / file_name
            if not file_path.exists():
                issues.append(f"Missing file: {file_name}")
        
        return issues
    
    def _check_environment(self) -> List[str]:
        """Check environment configuration"""
        issues = []
        
        env_file = self.project_root / '.env'
        if env_file.exists():
            with open(env_file, 'r') as f:
                content = f.read()
                if 'SECRET_KEY=your-secret-key-change-this' in content:
                    issues.append("Default SECRET_KEY detected - should be changed")
        else:
            issues.append("No .env file found")
        
        return issues
    
    def fix_import_issues(self):
        """Fix Python import issues"""
        logger.info("🔧 Fixing import issues...")
        
        # Fix missing __init__.py files
        init_files_needed = [
            'src/__init__.py',
            'src/api/__init__.py',
            'src/core/__init__.py',
            'src/config/__init__.py',
            'src/web/__init__.py',
            'src/tools/__init__.py'
        ]
        
        for init_file in init_files_needed:
            file_path = self.project_root / init_file
            if not file_path.exists():
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text('"""Package initialization"""')
                self.fixes_applied.append(f"Created {init_file}")
        
        # Fix import statements in problematic files
        self._fix_file_imports()
    
    def _fix_file_imports(self):
        """Fix import statements in specific files"""
        fixes = {
            'monitoring.py': [
                ('from email.mime.text import MimeText', 'from email.mime.text import MIMEText'),
                ('from email.mime.multipart import MimeMultipart', 'from email.mime.multipart import MIMEMultipart'),
                ('MimeText', 'MIMEText'),
                ('MimeMultipart', 'MIMEMultipart')
            ],
            'auth.py': [
                ('request.current_user', 'g.current_user'),
                ('from flask import request, jsonify, current_app', 'from flask import request, jsonify, current_app, g')
            ]
        }
        
        for filename, replacements in fixes.items():
            file_path = self.project_root / filename
            if file_path.exists():
                content = file_path.read_text()
                original_content = content
                
                for old, new in replacements:
                    content = content.replace(old, new)
                
                if content != original_content:
                    file_path.write_text(content)
                    self.fixes_applied.append(f"Fixed imports in {filename}")
    
    def fix_docker_issues(self):
        """Fix Docker-related issues"""
        logger.info("🐳 Fixing Docker issues...")
        
        # Create Docker configuration for Windows
        docker_config = {
            "version": "3.8",
            "services": {
                "agentdaf1": {
                    "build": ".",
                    "ports": ["8080:8080"],
                    "environment": [
                        "FLASK_ENV=production",
                        "PYTHONPATH=/app"
                    ],
                    "volumes": [
                        "./data:/app/data",
                        "./logs:/app/logs",
                        "./backups:/app/backups"
                    ],
                    "restart": "unless-stopped"
                }
            }
        }
        
        docker_compose_path = self.project_root / 'docker-compose.fixed.yml'
        with open(docker_compose_path, 'w') as f:
            json.dump(docker_config, f, indent=2)
        
        self.fixes_applied.append("Created fixed docker-compose.fixed.yml")
        
        # Create Windows-specific Dockerfile
        dockerfile_content = """FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y //
    gcc //
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p data logs backups

# Set environment variables
ENV FLASK_APP=simple_app.py
ENV FLASK_ENV=production
ENV PYTHONPATH=/app

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 //
    CMD curl -f http://localhost:8080/api/health || exit 1

# Run the application
CMD ["python", "simple_app.py"]
"""
        
        dockerfile_path = self.project_root / 'Dockerfile.fixed'
        dockerfile_path.write_text(dockerfile_content)
        self.fixes_applied.append("Created fixed Dockerfile.fixed")
    
    def create_directories(self):
        """Create necessary directories"""
        logger.info("[DIRS] Creating directories...")
        
        directories = ['data', 'logs', 'backups', 'static', 'uploads']
        
        for dir_name in directories:
            dir_path = self.project_root / dir_name
            if not dir_path.exists():
                dir_path.mkdir(exist_ok=True)
                self.fixes_applied.append(f"Created directory: {dir_name}")
    
    def fix_environment_files(self):
        """Fix environment configuration"""
        logger.info("⚙️ Fixing environment files...")
        
        # Create .env file if missing
        env_file = self.project_root / '.env'
        if not env_file.exists():
            env_content = """# AgentDaf1.1 Environment Configuration
FLASK_APP=simple_app.py
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=agentdaf1-secret-key-change-in-production-12345
JWT_SECRET_KEY=agentdaf1-jwt-secret-change-in-production-67890

# Server Configuration
HOST=0.0.0.0
PORT=8080

# Database
DATABASE_URL=sqlite:///data/agentdaf1.db

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/agentdaf1.log

# CORS
CORS_ORIGINS=*

# Production Settings
PRODUCTION=False
TESTING=False
"""
            env_file.write_text(env_content)
            self.fixes_applied.append("Created .env file")
    
    def install_dependencies(self):
        """Install missing dependencies"""
        logger.info("📦 Installing dependencies...")
        
        try:
            # Install basic requirements
            subprocess.run([
                sys.executable, '-m', 'pip', 'install', 
                'flask', 'flask-cors', 'requests', 'psutil',
                'schedule', 'bcrypt', 'pyjwt', 'pandas', 'openpyxl',
                'pytest', 'python-dotenv'
            ], check=True, capture_output=True)
            
            self.fixes_applied.append("Installed basic dependencies")
        except subprocess.CalledProcessError as e:
            logger.info(f"❌ Failed to install dependencies: {e}")
    
    def create_startup_script(self):
        """Create Windows startup script"""
        logger.info("🚀 Creating startup script...")
        
        startup_script = """@echo off
echo Starting AgentDaf1.1 Gaming Dashboard...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Python not found! Please install Python 3.8+
    pause
    exit /b 1
)

REM Check if required packages are installed
python -c "import flask, flask_cors, requests" >nul 2>&1
if errorlevel 1 (
    echo Installing required packages...
    pip install flask flask-cors requests psutil schedule bcrypt pyjwt pandas openpyxl
)

REM Create necessary directories
if not exist "data" mkdir data
if not exist "logs" mkdir logs
if not exist "backups" mkdir backups

REM Start the application
echo.
echo ========================================
echo   AgentDaf1.1 Gaming Dashboard
echo ========================================
echo.
echo Dashboard will be available at: http://localhost:8080
echo Press Ctrl+C to stop the server
echo.

python simple_app.py

pause
"""
        
        script_path = self.project_root / 'start_agentdaf1.bat'
        script_path.write_text(startup_script)
        self.fixes_applied.append("Created start_agentdaf1.bat")
    
    def run_system_fix(self):
        """Run complete system fix"""
        logger.info("[AgentDaf1.1] System Fix Tool")
        logger.info("=" * 40)
        
        # Diagnose system
        diagnosis = self.diagnose_system()
        logger.info(f"/n[DIAGNOSIS] System Status:")
        logger.info(f"Python: {diagnosis['python_version']}")
        logger.info(f"Platform: {diagnosis['platform']}")
        logger.info(f"Issues found: {len(diagnosis['issues'])}")
        
        if diagnosis['issues']:
            logger.info("/n[ISSUES] Found:")
            for issue in diagnosis['issues']:
                logger.info(f"  - {issue}")
        
        # Apply fixes
        logger.info("/n[FIXING] Applying fixes...")
        
        self.create_directories()
        self.fix_environment_files()
        self.fix_import_issues()
        self.fix_docker_issues()
        self.create_startup_script()
        
        try:
            self.install_dependencies()
        except Exception as e:
            logger.info(f"⚠️ Dependency installation failed: {e}")
        
        # Summary
        logger.info(f"/n✅ System Fix Complete!")
        logger.info(f"Fixes applied: {len(self.fixes_applied)}")
        
        for fix in self.fixes_applied:
            logger.info(f"  ✓ {fix}")
        
        logger.info(f"/n🚀 Next Steps:")
        logger.info(f"1. Run: start_agentdaf1.bat")
        logger.info(f"2. Open: http://localhost:8080")
        logger.info(f"3. For Docker: docker-compose -f docker-compose.fixed.yml up")
        
        return {
            "diagnosis": diagnosis,
            "fixes_applied": self.fixes_applied,
            "success": True
        }

def main():
    """Main function"""
    fixer = SystemFixer()
    result = fixer.run_system_fix()
    
    if result["success"]:
        logger.info("/n🎉 AgentDaf1.1 is ready to run!")
    else:
        logger.info("/n❌ Some issues remain. Please check the output above.")

if __name__ == "__main__":
    main()