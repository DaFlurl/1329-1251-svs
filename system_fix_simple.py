#!/usr/bin/env python3
"""
AgentDaf1.1 System Fix Tool - Simplified Version
Fixes Docker, import, and system integration issues
"""

import os
import sys
import subprocess
from pathlib import Path

class SystemFixer:
    """System issue fixer for AgentDaf1.1"""
    
    def __init__(self):
        self.project_root = Path.cwd()
        self.fixes_applied = []
        
    def create_directories(self):
        """Create necessary directories"""
        logger.info("[DIRS] Creating directories...")
        directories = [
            "backups",
            "logs",
            "uploads",
            "static/uploads",
            "instance"
        ]
        
        for directory in directories:
            dir_path = self.project_root / directory
            if not dir_path.exists():
                dir_path.mkdir(parents=True, exist_ok=True)
                self.fixes_applied.append(f"Created directory: {directory}")
                logger.info(f"  Created: {directory}")
    
    def fix_environment_files(self):
        """Fix environment files"""
        logger.info("[ENV] Fixing environment files...")
        
        # Create .env file if missing
        env_file = self.project_root / ".env"
        if not env_file.exists():
            env_content = """# AgentDaf1.1 Environment Configuration
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=agentdaf1-secret-key-change-in-production
DATABASE_URL=sqlite:///agentdaf1.db
JWT_SECRET_KEY=jwt-secret-key-change-in-production
"""
            env_file.write_text(env_content)
            self.fixes_applied.append("Created .env file")
            logger.info("  Created: .env")
    
    def fix_imports(self):
        """Fix import issues"""
        logger.info("[IMPORTS] Fixing import issues...")
        
        # Fix monitoring.py imports
        monitoring_file = self.project_root / "monitoring.py"
        if monitoring_file.exists():
            content = monitoring_file.read_text()
            if "from email.mime.text import MimeText" in content:
                content = content.replace("from email.mime.text import MimeText", "from email.mime.text import MIMEText")
                content = content.replace("MimeText", "MIMEText")
                monitoring_file.write_text(content)
                self.fixes_applied.append("Fixed monitoring.py imports")
                logger.info("  Fixed: monitoring.py imports")
    
    def run_system_fix(self):
        """Run complete system fix"""
        logger.info("[AgentDaf1.1] System Fix Tool")
        logger.info("=" * 40)
        
        # Apply fixes
        self.create_directories()
        self.fix_environment_files()
        self.fix_imports()
        
        logger.info("/n[COMPLETE] Fixes Applied:")
        for fix in self.fixes_applied:
            logger.info(f"  - {fix}")
        
        logger.info(f"/nTotal fixes applied: {len(self.fixes_applied)}")
        return {"fixes_applied": self.fixes_applied}

def main():
    """Main function"""
    fixer = SystemFixer()
    result = fixer.run_system_fix()
    return result

if __name__ == "__main__":
    main()