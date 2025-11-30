"""
GitHub Integration for AgentDaf1.1
Handles GitHub API operations for file synchronization
"""

import requests
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import base64
import os

logger = logging.getLogger(__name__)

class GitHubIntegration:
    """GitHub API integration for file management"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.token = config.get('GITHUB_TOKEN')
        self.repo_owner = config.get('GITHUB_REPO_OWNER')
        self.repo_name = config.get('GITHUB_REPO_NAME')
        self.api_base = 'https://api.github.com'
        
        if not all([self.token, self.repo_owner, self.repo_name]):
            logger.warning("GitHub integration not fully configured")
    
    def update_files(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update files in GitHub repository
        
        Args:
            data: Update data with file information
            
        Returns:
            Update result
        """
        try:
            if not self._is_configured():
                return {
                    'success': False,
                    'error': 'GitHub integration not configured'
                }
            
            results = []
            
            # Update dashboard files
            if 'dashboards' in data:
                for dashboard in data['dashboards']:
                    result = self._update_file(
                        path=dashboard['path'],
                        content=dashboard['content'],
                        message=f"Update dashboard {dashboard['name']}"
                    )
                    results.append(result)
            
            # Update data files
            if 'data_files' in data:
                for data_file in data['data_files']:
                    result = self._update_file(
                        path=data_file['path'],
                        content=data_file['content'],
                        message=f"Update data {data_file['name']}"
                    )
                    results.append(result)
            
            # Update documentation
            if 'docs' in data:
                for doc in data['docs']:
                    result = self._update_file(
                        path=doc['path'],
                        content=doc['content'],
                        message=f"Update documentation {doc['name']}"
                    )
                    results.append(result)
            
            success_count = sum(1 for r in results if r['success'])
            total_count = len(results)
            
            return {
                'success': success_count > 0,
                'message': f'Updated {success_count}/{total_count} files',
                'results': results,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"GitHub update error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _update_file(self, path: str, content: str, message: str) -> Dict[str, Any]:
        """
        Update a single file in repository
        
        Args:
            path: File path in repository
            content: File content
            message: Commit message
            
        Returns:
            Update result
        """
        try:
            # Get current file SHA
            url = f"{self.api_base}/repos/{self.repo_owner}/{self.repo_name}/contents/{path}"
            headers = {
                'Authorization': f'token {self.token}',
                'Accept': 'application/vnd.github.v3+json'
            }
            
            # Get file info
            response = requests.get(url, headers=headers)
            sha = None
            if response.status_code == 200:
                sha = response.json().get('sha')
            
            # Prepare file data
            file_data = {
                'message': message,
                'content': base64.b64encode(content.encode()).decode(),
                'sha': sha
            }
            
            # Update file
            response = requests.put(url, json=file_data, headers=headers)
            
            if response.status_code in [200, 201]:
                logger.info(f"Successfully updated {path}")
                return {
                    'success': True,
                    'path': path,
                    'message': 'File updated successfully'
                }
            else:
                logger.error(f"Failed to update {path}: {response.text}")
                return {
                    'success': False,
                    'path': path,
                    'error': f"HTTP {response.status_code}: {response.text}"
                }
                
        except Exception as e:
            logger.error(f"Error updating file {path}: {str(e)}")
            return {
                'success': False,
                'path': path,
                'error': str(e)
            }
    
    def create_repository(self, repo_name: str, description: str = "", private: bool = False) -> Dict[str, Any]:
        """
        Create a new repository
        
        Args:
            repo_name: Repository name
            description: Repository description
            private: Whether repository should be private
            
        Returns:
            Creation result
        """
        try:
            if not self._is_configured():
                return {
                    'success': False,
                    'error': 'GitHub integration not configured'
                }
            
            url = f"{self.api_base}/user/repos"
            headers = {
                'Authorization': f'token {self.token}',
                'Accept': 'application/vnd.github.v3+json'
            }
            
            data = {
                'name': repo_name,
                'description': description,
                'private': private,
                'auto_init': True
            }
            
            response = requests.post(url, json=data, headers=headers)
            
            if response.status_code == 201:
                repo_data = response.json()
                logger.info(f"Repository {repo_name} created successfully")
                return {
                    'success': True,
                    'repository': {
                        'name': repo_data['name'],
                        'url': repo_data['html_url'],
                        'clone_url': repo_data['clone_url']
                    }
                }
            else:
                logger.error(f"Failed to create repository: {response.text}")
                return {
                    'success': False,
                    'error': f"HTTP {response.status_code}: {response.text}"
                }
                
        except Exception as e:
            logger.error(f"Error creating repository: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_repository_info(self) -> Dict[str, Any]:
        """
        Get repository information
        
        Returns:
            Repository information
        """
        try:
            if not self._is_configured():
                return {
                    'success': False,
                    'error': 'GitHub integration not configured'
                }
            
            url = f"{self.api_base}/repos/{self.repo_owner}/{self.repo_name}"
            headers = {
                'Authorization': f'token {self.token}',
                'Accept': 'application/vnd.github.v3+json'
            }
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                repo_data = response.json()
                return {
                    'success': True,
                    'repository': {
                        'name': repo_data['name'],
                        'full_name': repo_data['full_name'],
                        'description': repo_data['description'],
                        'private': repo_data['private'],
                        'html_url': repo_data['html_url'],
                        'clone_url': repo_data['clone_url'],
                        'default_branch': repo_data['default_branch'],
                        'stars': repo_data['stargazers_count'],
                        'forks': repo_data['forks_count'],
                        'created_at': repo_data['created_at'],
                        'updated_at': repo_data['updated_at']
                    }
                }
            else:
                return {
                    'success': False,
                    'error': f"HTTP {response.status_code}: {response.text}"
                }
                
        except Exception as e:
            logger.error(f"Error getting repository info: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def list_files(self, path: str = "") -> Dict[str, Any]:
        """
        List files in repository path
        
        Args:
            path: Path to list (default: root)
            
        Returns:
            File list
        """
        try:
            if not self._is_configured():
                return {
                    'success': False,
                    'error': 'GitHub integration not configured'
                }
            
            url = f"{self.api_base}/repos/{self.repo_owner}/{self.repo_name}/contents/{path}"
            headers = {
                'Authorization': f'token {self.token}',
                'Accept': 'application/vnd.github.v3+json'
            }
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                files_data = response.json()
                files = []
                
                for item in files_data:
                    if item['type'] == 'file':
                        files.append({
                            'name': item['name'],
                            'path': item['path'],
                            'size': item['size'],
                            'download_url': item['download_url'],
                            'type': 'file'
                        })
                    elif item['type'] == 'dir':
                        files.append({
                            'name': item['name'],
                            'path': item['path'],
                            'type': 'directory'
                        })
                
                return {
                    'success': True,
                    'files': files,
                    'path': path
                }
            else:
                return {
                    'success': False,
                    'error': f"HTTP {response.status_code}: {response.text}"
                }
                
        except Exception as e:
            logger.error(f"Error listing files: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _is_configured(self) -> bool:
        """Check if GitHub integration is properly configured"""
        return all([
            self.token is not None,
            self.repo_owner is not None,
            self.repo_name is not None
        ])
    
    def get_webhook_info(self) -> Dict[str, Any]:
        """
        Get webhook information for repository
        
        Returns:
            Webhook information
        """
        try:
            if not self._is_configured():
                return {
                    'success': False,
                    'error': 'GitHub integration not configured'
                }
            
            url = f"{self.api_base}/repos/{self.repo_owner}/{self.repo_name}/hooks"
            headers = {
                'Authorization': f'token {self.token}',
                'Accept': 'application/vnd.github.v3+json'
            }
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                webhooks = response.json()
                return {
                    'success': True,
                    'webhooks': webhooks,
                    'count': len(webhooks)
                }
            else:
                return {
                    'success': False,
                    'error': f"HTTP {response.status_code}: {response.text}"
                }
                
        except Exception as e:
            logger.error(f"Error getting webhook info: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }