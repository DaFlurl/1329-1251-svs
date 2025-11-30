#!/usr/bin/env python3
"""
GitHub Repository Management Tool
Manages GitHub operations for AgentDaf1.1 project
"""

import os
import sys
import json
import subprocess
import requests
from datetime import datetime

class GitHubManager:
    def __init__(self):
        self.config_file = "github_config.json"
        self.config = self.load_config()
        
    def load_config(self):
        """Load GitHub configuration"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        
        # Default configuration with token
        return {
            "username": "FlorinStrobel",
            "repository": "AgentDaf1.1",
            "token": "ghp_GHvP16Zobp2020ZEq9JKqXcEUPYUy70PXdSz",
            "api_url": "https://api.github.com"
        }
    
    def save_config(self):
        """Save GitHub configuration"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def check_repository_exists(self):
        """Check if repository exists on GitHub"""
        try:
            url = f"{self.config['api_url']}/repos/{self.config['username']}/{self.config['repository']}"
            response = requests.get(url, timeout=10)
            return response.status_code == 200
        except:
            return False
    
    def create_repository(self):
        """Create repository on GitHub"""
        if not self.config.get("token"):
            print("GitHub token required for repository creation")
            print("Please set GITHUB_TOKEN environment variable or update config")
            return False
        
        try:
            headers = {
                "Authorization": f"token {self.config['token']}",
                "Accept": "application/vnd.github.v3+json"
            }
            
            data = {
                "name": self.config["repository"],
                "description": "AgentDaf1.1 - Advanced Excel Data Processing Platform with 3D Dashboard",
                "private": False,
                "auto_init": False
            }
            
            response = requests.post(
                f"{self.config['api_url']}/user/repos",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 201:
                print("Repository created successfully")
                return True
            else:
                print(f"Failed to create repository: {response.status_code}")
                print(response.text)
                return False
                
        except Exception as e:
            print(f"Error creating repository: {e}")
            return False
    
    def setup_remote(self):
        """Setup git remote"""
        try:
            # Remove existing remote
            subprocess.run(["git", "remote", "remove", "origin"], 
                         capture_output=True, check=False)
            
            # Add new remote
            remote_url = f"https://github.com/{self.config['username']}/{self.config['repository']}.git"
            result = subprocess.run(["git", "remote", "add", "origin", remote_url],
                                 capture_output=True, text=True, check=True)
            
            print(f"Remote configured: {remote_url}")
            return True
            
        except Exception as e:
            print(f"Error setting up remote: {e}")
            return False
    
    def push_to_github(self, branch="feature/user-profile-enhancement-2"):
        """Push current branch to GitHub"""
        try:
            # Push with upstream tracking
            result = subprocess.run(
                ["git", "push", "-u", "origin", branch],
                capture_output=True, text=True, check=True
            )
            
            print(f"Successfully pushed to GitHub: {branch}")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"Push failed: {e}")
            print(f"Stdout: {e.stdout}")
            print(f"Stderr: {e.stderr}")
            return False
    
    def sync_repository(self):
        """Complete repository synchronization"""
        print("Starting GitHub synchronization...")
        print("=" * 50)
        
        # Check if repository exists
        print("Checking repository existence...")
        if not self.check_repository_exists():
            print("Repository not found, creating...")
            if not self.create_repository():
                return False
        
        # Setup remote
        print("Setting up git remote...")
        if not self.setup_remote():
            return False
        
        # Push to GitHub
        print("Pushing to GitHub...")
        if not self.push_to_github():
            return False
        
        print("GitHub synchronization complete!")
        return True
    
    def show_status(self):
        """Show current status"""
        print("GitHub Manager Status:")
        print(f"  Username: {self.config['username']}")
        print(f"  Repository: {self.config['repository']}")
        print(f"  API URL: {self.config['api_url']}")
        print(f"  Token Configured: {'Yes' if self.config.get('token') else 'No'}")
        
        # Check git status
        try:
            result = subprocess.run(["git", "status", "--porcelain"],
                                 capture_output=True, text=True, check=True)
            changes = len(result.stdout.strip().split('\n')) if result.stdout.strip() else 0
            print(f"  Git Changes: {changes}")
            
            # Current branch
            result = subprocess.run(["git", "branch", "--show-current"],
                                 capture_output=True, text=True, check=True)
            print(f"  Current Branch: {result.stdout.strip()}")
            
        except:
            print("  Git Status: Unable to determine")
        
        # Repository exists check
        exists = self.check_repository_exists()
        print(f"  Remote Repository: {'Exists' if exists else 'Not Found'}")
    
    def interactive_setup(self):
        """Interactive setup for GitHub configuration"""
        print("GitHub Repository Setup")
        print("=" * 30)
        
        # Get username
        username = input(f"GitHub username [{self.config['username']}]: ").strip()
        if username:
            self.config['username'] = username
        
        # Get repository name
        repo = input(f"Repository name [{self.config['repository']}]: ").strip()
        if repo:
            self.config['repository'] = repo
        
        # Get token
        token = input("GitHub token (leave blank to use GITHUB_TOKEN env): ").strip()
        if token:
            self.config['token'] = token
        elif os.getenv('GITHUB_TOKEN'):
            self.config['token'] = os.getenv('GITHUB_TOKEN')
        
        # Save configuration
        self.save_config()
        print("Configuration saved")

def main():
    manager = GitHubManager()
    
    if len(sys.argv) < 2:
        print("GitHub Repository Management Tool")
        print("Usage:")
        print("  python github_tool.py status     - Show current status")
        print("  python github_tool.py setup      - Interactive setup")
        print("  python github_tool.py sync       - Sync to GitHub")
        print("  python github_tool.py push       - Push current branch")
        return
    
    command = sys.argv[1].lower()
    
    if command == "status":
        manager.show_status()
    elif command == "setup":
        manager.interactive_setup()
    elif command == "sync":
        manager.sync_repository()
    elif command == "push":
        branch = sys.argv[2] if len(sys.argv) > 2 else "feature/user-profile-enhancement-2"
        manager.push_to_github(branch)
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()