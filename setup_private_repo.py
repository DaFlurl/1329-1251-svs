#!/usr/bin/env python3
"""
AgentDaf Repository Manager
Manages private AgentDaf repository and public dashboard deployment
"""

import os
import shutil
import subprocess
from pathlib import Path
from datetime import datetime
import json

class RepoManager:
    def __init__(self):
        self.agentdaf_root = Path("C:/Users/flori/Desktop/AgentDaf")
        self.dashboard_root = Path("C:/Users/flori/Desktop/AgentDaf1/github-dashboard")
        self.private_repo_name = "AgentDaf"
        self.public_dashboard_repo = "1329-1251-svs"
        
        # Files that should be public (dashboard only)
        self.public_files = [
            "scoreboard.html",
            "scoreboard-data.json", 
            "index.html",
            "README.md"
        ]
        
        # Files that should stay private
        self.private_files = [
            "mcp_server.py",
            "enhanced_mcp_server.py",
            "excel_workflow.py", 
            "docker_mcp_tools.py",
            "file_history_manager.py",
            "history_api_server.py",
            "config_manager.py",
            "fix_scoreboard_data.py",
            "serve.py",
            "requirements.txt",
            "package.json",
            ".env",
            "file_history/",
            "*.pyc",
            "*.log"
        ]
    
    def create_private_repo_structure(self):
        """Create the private AgentDaf repository structure"""
        print("Creating private AgentDaf repository structure...")
        
        # Create main directories
        dirs_to_create = [
            "mcp_tools",
            "excel_tools", 
            "docker_tools",
            "workflows",
            "scripts",
            "config",
            "data",
            "logs",
            "tests",
            "docs",
            "dashboard"
        ]
        
        # Create root directory first
        self.agentdaf_root.mkdir(exist_ok=True, parents=True)
        
        for dir_name in dirs_to_create:
            dir_path = self.agentdaf_root / dir_name
            dir_path.mkdir(exist_ok=True, parents=True)
            print(f"Created directory: {dir_path}")
        
        # Move dashboard files to dashboard subdirectory
        dashboard_dest = self.agentdaf_root / "dashboard"
        self.copy_dashboard_files(dashboard_dest)
        
        # Move private files to appropriate locations
        self.organize_private_files()
        
        # Create .gitignore for private repo
        self.create_private_gitignore()
        
        # Create README for private repo
        self.create_private_readme()
        
        print("Private repository structure created successfully!")
    
    def copy_dashboard_files(self, dest_dir):
        """Copy only public dashboard files"""
        print("Copying public dashboard files...")
        
        dest_dir.mkdir(exist_ok=True)
        
        for file_name in self.public_files:
            src_file = self.dashboard_root / file_name
            if src_file.exists():
                if src_file.is_file():
                    shutil.copy2(src_file, dest_dir / file_name)
                    print(f"Copied: {file_name}")
                else:
                    shutil.copytree(src_file, dest_dir / file_name, dirs_exist_ok=True)
                    print(f"Copied directory: {file_name}")
        
        # Copy the new scoreboard as main
        new_scoreboard = self.dashboard_root / "scoreboard_new.html"
        if new_scoreboard.exists():
            shutil.copy2(new_scoreboard, dest_dir / "scoreboard.html")
            print("Copied: scoreboard_new.html -> scoreboard.html")
    
    def organize_private_files(self):
        """Organize private files into appropriate directories"""
        print("Organizing private files...")
        
        # MCP tools
        mcp_files = [
            "mcp_server.py",
            "enhanced_mcp_server.py", 
            "docker_mcp_tools.py"
        ]
        mcp_dest = self.agentdaf_root / "mcp_tools"
        for file_name in mcp_files:
            src_file = self.dashboard_root / file_name
            if src_file.exists():
                shutil.copy2(src_file, mcp_dest / file_name)
                print(f"Moved to mcp_tools: {file_name}")
        
        # Excel tools
        excel_files = ["excel_workflow.py"]
        excel_dest = self.agentdaf_root / "excel_tools"
        for file_name in excel_files:
            src_file = self.dashboard_root / file_name
            if src_file.exists():
                shutil.copy2(src_file, excel_dest / file_name)
                print(f"Moved to excel_tools: {file_name}")
        
        # Scripts
        script_files = [
            "file_history_manager.py",
            "history_api_server.py",
            "config_manager.py",
            "fix_scoreboard_data.py",
            "serve.py"
        ]
        scripts_dest = self.agentdaf_root / "scripts"
        for file_name in script_files:
            src_file = self.dashboard_root / file_name
            if src_file.exists():
                shutil.copy2(src_file, scripts_dest / file_name)
                print(f"Moved to scripts: {file_name}")
        
        # Config
        config_files = ["requirements.txt", "package.json", ".env"]
        config_dest = self.agentdaf_root / "config"
        for file_name in config_files:
            src_file = self.dashboard_root / file_name
            if src_file.exists():
                shutil.copy2(src_file, config_dest / file_name)
                print(f"Moved to config: {file_name}")
    
    def create_private_gitignore(self):
        """Create .gitignore for private repository"""
        gitignore_content = """# AgentDaf Private Repository

# Sensitive data
.env
*.key
*.pem
config/secrets/
logs/
data/private/

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Temporary files
*.tmp
*.temp
*.log
file_history/
backups/

# Node modules (if any)
node_modules/

# Build artifacts
build/
dist/
"""
        
        gitignore_path = self.agentdaf_root / ".gitignore"
        with open(gitignore_path, 'w', encoding='utf-8') as f:
            f.write(gitignore_content)
        print("Created private .gitignore")
    
    def create_private_readme(self):
        """Create README for private repository"""
        readme_content = f"""# AgentDaf - Private Repository

**⚠️ This is a private repository containing the complete AgentDaf system.**

## Repository Structure

```
AgentDaf/
├── mcp_tools/          # MCP server implementations
├── excel_tools/        # Excel processing tools
├── docker_tools/       # Docker management tools
├── workflows/          # Automation workflows
├── scripts/            # Utility scripts
├── config/             # Configuration files
├── data/               # Data files
├── logs/               # Log files
├── tests/              # Test files
├── docs/               # Documentation
└── dashboard/          # Public dashboard (deployed separately)
```

## Components

### MCP Tools
- **mcp_server.py**: Basic MCP server
- **enhanced_mcp_server.py**: Enhanced MCP with additional features
- **docker_mcp_tools.py**: Docker management MCP tools

### Excel Tools
- **excel_workflow.py**: Excel file processing and data extraction

### Scripts
- **file_history_manager.py**: File version tracking and backup system
- **history_api_server.py**: REST API for file history
- **config_manager.py**: Configuration management
- **fix_scoreboard_data.py**: Data correction utilities
- **serve.py**: Local development server

### Dashboard
The public dashboard is located in the `dashboard/` directory and is deployed to a separate public repository.

## Security Notice

This repository contains:
- Sensitive configuration files
- Private API keys and credentials
- Internal tools and scripts
- Development and testing code

**Do not make this repository public!**

## Deployment

### Private Components
- MCP servers run on private infrastructure
- Excel processing tools run locally
- History API server runs on private network

### Public Dashboard
- Located in `dashboard/` directory
- Deployed to separate public repository: {self.public_dashboard_repo}
- Only contains frontend files and public data

## Setup

1. Clone this private repository
2. Install dependencies: `pip install -r config/requirements.txt`
3. Configure environment: Copy `config/.env.example` to `config/.env`
4. Run MCP servers: `python mcp_tools/enhanced_mcp_server.py`
5. Start dashboard: `python scripts/serve.py`

## Support

For internal use only. Contact the development team for assistance.
"""
        
        readme_path = self.agentdaf_root / "README.md"
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        print("Created private README.md")
    
    def create_dashboard_deployment_script(self):
        """Create script to deploy only dashboard to public repo"""
        script_content = f'''#!/usr/bin/env python3
"""
Dashboard Deployment Script
Deploys only the dashboard files to the public GitHub repository
"""

import os
import shutil
import subprocess
from pathlib import Path
from datetime import datetime

class DashboardDeployer:
    def __init__(self):
        self.source_dir = Path("C:/Users/flori/Desktop/AgentDaf/dashboard")
        self.public_repo_dir = Path("C:/Users/flori/Desktop/AgentDaf1/github-dashboard")
        self.public_repo_name = "{self.public_dashboard_repo}"
        
        # Files to deploy
        self.deploy_files = [
            "scoreboard.html",
            "scoreboard-data.json",
            "index.html",
            "README.md"
        ]
    
    def deploy_dashboard(self):
        """Deploy dashboard to public repository"""
        print("Starting dashboard deployment...")
        
        # Update data from Excel if needed
        self.update_dashboard_data()
        
        # Copy files to public repo
        self.copy_dashboard_files()
        
        # Commit and push to public repo
        self.commit_and_push()
        
        print("Dashboard deployment completed!")
            print(f"Public URL: https://daflurl.github.io/{self.public_dashboard_repo}")
    
    def update_dashboard_data(self):
        """Update dashboard data from Excel source"""
        try:
            # Run data fix script
            result = subprocess.run([
                "python", "scripts/fix_scoreboard_data.py"
            ], cwd=self.source_dir.parent, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("Dashboard data updated successfully")
            else:
                print(f"Warning: Data update failed: {{result.stderr}}")
        except Exception as e:
            print(f"Warning: Could not update data: {{e}}")
    
    def copy_dashboard_files(self):
        """Copy dashboard files to public repository"""
        print("Copying dashboard files...")
        
        for file_name in self.deploy_files:
            src_file = self.source_dir / file_name
            dest_file = self.public_repo_dir / file_name
            
            if src_file.exists():
                shutil.copy2(src_file, dest_file)
                print(f"Copied: {{file_name}}")
            else:
                print(f"Warning: {{file_name}} not found in source")
    
    def commit_and_push(self):
        """Commit and push changes to public repository"""
        print("Committing and pushing to public repository...")
        
        try:
            os.chdir(self.public_repo_dir)
            
            # Add all changes
            subprocess.run(["git", "add", "."], check=True)
            
            # Commit with timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            commit_message = f"Update dashboard - {{timestamp}}"
            
            subprocess.run(["git", "commit", "-m", commit_message], check=True)
            
            # Push to origin
            subprocess.run(["git", "push", "origin", "main"], check=True)
            
            print("Changes pushed to public repository successfully!")
            
        except subprocess.CalledProcessError as e:
            print(f"Error during git operations: {{e}}")
        except Exception as e:
            print(f"Error: {{e}}")

if __name__ == "__main__":
    deployer = DashboardDeployer()
    deployer.deploy_dashboard()
'''
        
        script_path = self.agentdaf_root / "scripts" / "deploy_dashboard.py"
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script_content)
        print("Created dashboard deployment script")
    
    def setup_private_git_repo(self):
        """Initialize private Git repository"""
        print("Setting up private Git repository...")
        
        try:
            os.chdir(self.agentdaf_root)
            
            # Initialize git repo
            subprocess.run(["git", "init"], check=True)
            
            # Add all files
            subprocess.run(["git", "add", "."], check=True)
            
            # Initial commit
            subprocess.run(["git", "commit", "-m", "Initial commit - AgentDaf private repository"], check=True)
            
            print("Private Git repository initialized successfully!")
            
            # Instructions for remote setup
            print("//nNext steps:")
            print(f"1. Create private repository on GitHub: {self.private_repo_name}")
            print("2. Add remote: git remote add origin <your-private-repo-url>")
            print("3. Push: git push -u origin main")
            
        except subprocess.CalledProcessError as e:
            print(f"Error setting up Git repository: {e}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    manager = RepoManager()
    
    print("=== AgentDaf Repository Setup ===")
    print("This will create a private repository structure and organize files accordingly.")
    print()
    
    # Create private repo structure
    manager.create_private_repo_structure()
    
    # Create deployment script
    manager.create_dashboard_deployment_script()
    
    # Setup Git repository
    manager.setup_private_git_repo()
    
    print()
    print("=== Setup Complete ===")
    print("Private repository structure created at:", manager.agentdaf_root)
    print("Public dashboard will be deployed from:", manager.dashboard_root)
    print()
    print("Next steps:")
    print("1. Create private GitHub repository")
    print("2. Push private repository to GitHub")
    print("3. Use deploy_dashboard.py to update public dashboard")