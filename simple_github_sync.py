#!/usr/bin/env python3
"""
Simple GitHub Sync Tool
Direct GitHub synchronization without Docker
"""

import os
import sys
import subprocess
import json
from datetime import datetime

class SimpleGitHubSync:
    def __init__(self):
        self.config = {
            "username": "FlorinStrobel",
            "repository": "AgentDaf1.1",
            "branch": "feature/user-profile-enhancement-2"
        }
    
    def check_git_status(self):
        """Check current git status"""
        print("Checking Git Status...")
        try:
            # Current branch
            result = subprocess.run(["git", "branch", "--show-current"], 
                                  capture_output=True, text=True, check=True)
            print(f"Current Branch: {result.stdout.strip()}")
            
            # Status
            result = subprocess.run(["git", "status", "--porcelain"], 
                                  capture_output=True, text=True, check=True)
            if not result.stdout.strip():
                print("Status: Clean (all changes committed)")
                return True
            else:
                print("Status: Uncommitted changes exist")
                return False
                
        except Exception as e:
            print(f"Error checking status: {e}")
            return False
    
    def commit_changes(self):
        """Commit all changes"""
        print("Committing changes...")
        try:
            subprocess.run(["git", "add", "-A"], check=True)
            commit_message = f"Update 3D enhancements - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            subprocess.run(["git", "commit", "-m", commit_message], check=True)
            print("Changes committed successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error committing changes: {e}")
            return False
    
    def setup_github_token(self, token):
        """Setup GitHub token for authentication"""
        print("Setting up GitHub authentication...")
        try:
            remote_url = f"https://{token}@github.com/{self.config['username']}/{self.config['repository']}.git"
            subprocess.run(["git", "remote", "set-url", "origin", remote_url], check=True)
            print("GitHub authentication configured")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error setting up authentication: {e}")
            return False
    
    def push_to_github(self):
        """Push to GitHub"""
        print("Pushing to GitHub...")
        try:
            subprocess.run(["git", "push", "-u", "origin", self.config['branch']], 
                         check=True, capture_output=True)
            print("Successfully pushed to GitHub!")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Push failed: {e}")
            print(f"Stderr: {e.stderr.decode() if e.stderr else 'No error details'}")
            return False
    
    def create_repository_instructions(self):
        """Create instructions for manual repository creation"""
        instructions = f"""
# Manual Repository Creation Instructions

If GitHub push fails, create the repository manually:

1. Go to https://github.com/new
2. Repository name: {self.config['repository']}
3. Description: AgentDaf1.1 - Advanced Excel Data Processing Platform with 3D Dashboard
4. Make it Public
5. DO NOT initialize with README (we have code already)
6. Click "Create repository"
7. Run these commands:
   git remote set-url origin https://YOUR_TOKEN@github.com/{self.config['username']}/{self.config['repository']}.git
   git push -u origin {self.config['branch']}

## Alternative: Use GitHub CLI
gh repo create {self.config['username']}/{self.config['repository']} --public --description "AgentDaf1.1 - Advanced Excel Data Processing Platform with 3D Dashboard"
git push -u origin {self.config['branch']}
"""
        with open("GITHUB_SETUP_INSTRUCTIONS.md", "w") as f:
            f.write(instructions)
        print("Created GITHUB_SETUP_INSTRUCTIONS.md")
    
    def sync_with_token(self, token):
        """Complete sync with provided token"""
        print("Starting GitHub Sync...")
        print("=" * 40)
        
        # Check status
        if not self.check_git_status():
            if not self.commit_changes():
                return False
        
        # Setup authentication
        if not self.setup_github_token(token):
            return False
        
        # Push to GitHub
        if not self.push_to_github():
            print("Push failed. Creating manual instructions...")
            self.create_repository_instructions()
            return False
        
        print("GitHub sync completed successfully!")
        return True
    
    def show_summary(self):
        """Show project summary"""
        print("AgentDaf1.1 - 3D Enhancement Project")
        print("=" * 40)
        print("Status: Ready for GitHub deployment")
        print("3D Components: 16 files")
        print("Branch: feature/user-profile-enhancement-2")
        print("Repository: AgentDaf1.1")
        print("Owner: FlorinStrobel")
        print()
        print("3D Features Ready:")
        print("- 3D Framework with CSS/JS")
        print("- 3D Navigation with parallax")
        print("- 3D File upload with effects")
        print("- 3D Notification system")
        print("- 3D Background with geometric shapes")
        print("- 3D Hover effects")
        print("- 3D Data visualization")
        print("- 3D Dashboard template")

def main():
    sync = SimpleGitHubSync()
    
    if len(sys.argv) < 2:
        print("Simple GitHub Sync Tool")
        print("Usage:")
        print("  python simple_github_sync.py status     - Show status")
        print("  python simple_github_sync.py sync TOKEN - Sync with token")
        print("  python simple_github_sync.py summary    - Show project summary")
        return
    
    command = sys.argv[1].lower()
    
    if command == "status":
        sync.check_git_status()
    elif command == "sync":
        if len(sys.argv) < 3:
            print("Error: GitHub token required")
            print("Usage: python simple_github_sync.py sync YOUR_GITHUB_TOKEN")
            return
        token = sys.argv[2]
        sync.sync_with_token(token)
    elif command == "summary":
        sync.show_summary()
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()