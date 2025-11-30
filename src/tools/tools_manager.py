"""
ToolsManager class for managing development and utility tools.
Provides centralized access to various development, testing, and deployment tools.
"""

import logging
import os
import json
import subprocess
import tempfile
import shutil
from typing import Dict, List, Optional, Any
from datetime import datetime

class ToolsManager:
    """Manages development and utility tools."""
    
    def __init__(self, config_manager=None, database_manager=None):
        """Initialize the ToolsManager.
        
        Args:
            config_manager: ConfigManager instance for configuration (optional)
            database_manager: DatabaseManager instance for database operations (optional)
        """
        self.config_manager = config_manager
        self.database_manager = database_manager
        self.logger = logging.getLogger(__name__)
        
    def run_linter(self, file_path: str = None) -> Dict[str, Any]:
        """Run code linter on specified file or directory.
        
        Args:
            file_path: Path to file or directory to lint
            
        Returns:
            Dictionary containing linter results
        """
        try:
            if not file_path:
                file_path = "."
                
            # Check if file/directory exists
            if not os.path.exists(file_path):
                return {
                    "success": False,
                    "error": f"File or directory not found: {file_path}",
                    "output": ""
                }
                
            # Determine file type for appropriate linter
            if os.path.isfile(file_path):
                file_ext = os.path.splitext(file_path)[1].lower()
                if file_ext == '.py':
                    tool = 'flake8'
                    cmd = ['flake8', file_path, '--max-line-length=100', '--ignore=E203,W503']
                elif file_ext in ['.js', '.ts', '.jsx', '.tsx']:
                    tool = 'eslint'
                    cmd = ['npx', 'eslint', file_path]
                elif file_ext in ['.json']:
                    tool = 'jsonlint' 
                    cmd = ['jsonlint', file_path]
                else:
                    return {
                        "success": False,
                        "error": f"Unsupported file type for linting: {file_ext}",
                        "output": ""
                    }
            else:
                # Directory - use flake8 on all Python files
                tool = 'flake8'
                cmd = ['flake8', file_path, '--max-line-length=100', '--ignore=E203,W503']
                
            # Run linter
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=os.path.dirname(file_path) if os.path.isfile(file_path) else file_path
            )
            
            output = result.stdout.strip() if result.stdout else ""
            error = result.stderr.strip() if result.stderr else ""
            
            return {
                "success": result.returncode == 0,
                "tool": tool,
                "command": ' '.join(cmd),
                "output": output,
                "error": error if result.returncode != 0 else "",
                "file_path": file_path
            }
            
        except Exception as e:
            self.logger.error(f"Linter execution failed: {str(e)}")
            return {
                "success": False,
                "error": f"Linter execution failed: {str(e)}",
                "output": ""
            }
    
    def run_tests(self, test_path: str = None, test_type: str = "unit") -> Dict[str, Any]:
        """Run tests and return results.
        
        Args:
            test_path: Path to test file or directory
            test_type: Type of tests (unit, integration, performance)
            
        Returns:
            Dictionary containing test results
        """
        try:
            if not test_path:
                test_path = "tests/"
                
            if not os.path.exists(test_path):
                return {
                    "success": False,
                    "error": f"Test path not found: {test_path}",
                    "output": "",
                    "results": []
                }
            
            # Check for pytest
            pytest_ini = os.path.join(test_path, 'pytest.ini')
            requirements_file = os.path.join(test_path, 'requirements.txt')
            
            # Determine test command based on available files
            if os.path.exists(requirements_file):
                cmd = ['python', '-m', 'pytest', test_path, '--cov=src', '--cov-report=term-missing']
            else:
                cmd = ['python', '-m', 'pytest', test_path]
            
            # Add test type specific parameters
            if test_type == "integration":
                cmd.extend(['-v', '--tb=short'])
            elif test_type == "performance":
                cmd.extend(['--benchmark-only'])
                
            # Run tests
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=os.path.dirname(test_path)
            )
            
            output = result.stdout.strip() if result.stdout else ""
            error = result.stderr.strip() if result.stderr else ""
            
            # Parse test results
            test_results = []
            if result.returncode == 0 and output:
                # Simple parsing of pytest output
                lines = output.split('/n')
                for line in lines:
                    if ' PASSED' in line or ' FAILED' in line or ' ERROR' in line:
                        test_results.append(line.strip())
                        
            return {
                "success": result.returncode == 0,
                "command": ' '.join(cmd),
                "output": output,
                "error": error if result.returncode != 0 else "",
                "test_type": test_type,
                "test_path": test_path,
                "results": test_results
            }
            
        except Exception as e:
            self.logger.error(f"Test execution failed: {str(e)}")
            return {
                "success": False,
                "error": f"Test execution failed: {str(e)}",
                "output": "",
                "results": []
            }
    
    def format_code(self, file_path: str, style_guide: str = "pep8") -> Dict[str, Any]:
        """Format code according to specified style guide.
        
        Args:
            file_path: Path to source code file
            style_guide: Style guide to follow (pep8, black, etc.)
            
        Returns:
            Dictionary containing formatting results
        """
        try:
            if not os.path.exists(file_path):
                return {
                    "success": False,
                    "error": f"File not found: {file_path}",
                    "output": ""
                }
                
            # Determine formatting tool based on style guide
            if style_guide.lower() == 'pep8':
                tool = 'autopep8'
                cmd = [tool, '--in-place', file_path]
            elif style_guide.lower() == 'black':
                tool = 'black'
                cmd = [tool, file_path]
            elif style_guide.lower() == 'isort':
                tool = 'isort'
                cmd = [tool, file_path, '--profile', 'black']
            else:
                return {
                    "success": False,
                    "error": f"Unsupported style guide: {style_guide}",
                    "output": ""
                }
                
            # Run formatter
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=os.path.dirname(file_path)
            )
            
            output = result.stdout.strip() if result.stdout else ""
            error = result.stderr.strip() if result.stderr else ""
            
            return {
                "success": result.returncode == 0,
                "tool": tool,
                "command": ' '.join(cmd),
                "output": output,
                "error": error if result.returncode != 0 else "",
                "file_path": file_path
            }
            
        except Exception as e:
            self.logger.error(f"Code formatting failed: {str(e)}")
            return {
                "success": False,
                "error": f"Code formatting failed: {str(e)}",
                "output": ""
            }
    
    def check_dependencies(self, requirements_file: str = "requirements.txt") -> Dict[str, Any]:
        """Check project dependencies for security and compatibility.
        
        Args:
            requirements_file: Path to requirements file
            
        Returns:
            Dictionary containing dependency analysis
        """
        try:
            if not os.path.exists(requirements_file):
                return {
                    "success": False,
                    "error": f"Requirements file not found: {requirements_file}",
                    "dependencies": [],
                    "warnings": [],
                    "recommendations": []
                }
                
            # Read requirements
            with open(requirements_file, 'r') as f:
                requirements = f.read().strip().split('/n')
                
            dependencies = []
            warnings = []
            recommendations = []
            
            for req in requirements:
                req = req.strip()
                if not req or req.startswith('#'):
                    continue
                    
                # Parse requirement (simplified)
                if '==' in req:
                    package_name = req.split('==')[0].strip()
                    version_spec = req.split('==')[1].strip() if '==' in req else ""
                else:
                    package_name = req.strip()
                    version_spec = ""
                    
                # Check for common security issues
                security_warnings = []
                if package_name in ['eval', 'exec', 'compile']:
                    security_warnings.append(f"Security risk: {package_name} allows arbitrary code execution")
                if 'password' in package_name.lower():
                    security_warnings.append(f"Security risk: {package_name} may handle passwords")
                if version_spec and version_spec.startswith('0.'):
                    warnings.append(f"Development version: {package_name} {version_spec}")
                    
                dependencies.append({
                    "package": package_name,
                    "version": version_spec,
                    "security_warnings": security_warnings
                })
                
            return {
                "success": True,
                "dependencies": dependencies,
                "warnings": warnings,
                "recommendations": recommendations
            }
            
        except Exception as e:
            self.logger.error(f"Dependency check failed: {str(e)}")
            return {
                "success": False,
                "error": f"Dependency check failed: {str(e)}",
                "dependencies": [],
                "warnings": [],
                "recommendations": []
            }
    
    def generate_documentation(self, source_dir: str, output_dir: str = "docs/") -> Dict[str, Any]:
        """Generate documentation from source code.
        
        Args:
            source_dir: Directory containing source code
            output_dir: Directory to save documentation
            
        Returns:
            Dictionary containing documentation generation results
        """
        try:
            if not os.path.exists(source_dir):
                return {
                    "success": False,
                    "error": f"Source directory not found: {source_dir}",
                    "output": ""
                }
                
            # Create output directory if it doesn't exist
            os.makedirs(output_dir, exist_ok=True)
            
            # Find Python files to document
            python_files = []
            for root, dirs, files in os.walk(source_dir):
                for file in files:
                    if file.endswith('.py'):
                        python_files.append(os.path.join(root, file))
            
            if not python_files:
                return {
                    "success": False,
                    "error": "No Python files found in source directory",
                    "output": ""
                }
            
            # Generate documentation for each file
            doc_files = []
            for py_file in python_files:
                try:
                    # Read file content
                    with open(py_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Generate docstring-based documentation
                    doc_content = self._generate_file_docs(py_file, content)
                    
                    # Determine output file path
                    rel_path = os.path.relpath(py_file, source_dir)
                    doc_path = os.path.join(output_dir, rel_path.replace('.py', '.md'))
                    
                    # Write documentation
                    with open(doc_path, 'w', encoding='utf-8') as f:
                        f.write(doc_content)
                        
                    doc_files.append(doc_path)
                    
                except Exception as e:
                    self.logger.warning(f"Failed to generate docs for {py_file}: {str(e)}")
                    
            return {
                "success": True,
                "files_documented": len(python_files),
                "documentation_files": doc_files,
                "output_dir": output_dir
            }
            
        except Exception as e:
            self.logger.error(f"Documentation generation failed: {str(e)}")
            return {
                "success": False,
                "error": f"Documentation generation failed: {str(e)}",
                "output": ""
            }
    
    def _generate_file_docs(self, file_path: str, content: str) -> str:
        """Generate documentation for a single Python file.
        
        Args:
            file_path: Path to the Python file
            content: File content
            
        Returns:
            Generated documentation content
        """
        try:
            import ast
            
            # Parse the Python file
            tree = ast.parse(content)
            
            # Extract module docstring
            module_docstring = ast.get_docstring(tree)
            
            # Extract classes and functions
            classes = []
            functions = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    classes.append({
                        "name": node.name,
                        "docstring": ast.get_docstring(node),
                        "line": node.lineno
                    })
                elif isinstance(node, ast.FunctionDef):
                    # Get function signature
                    args = []
                    for arg in node.args.args:
                        arg_type = ast.unparse(arg.annotation).value if arg.annotation else "Any"
                        args.append(f"{arg.arg}: {arg_type}")
                    
                    return_type = ast.unparse(node.returns).value if node.returns else "Any"
                    
                    functions.append({
                        "name": node.name,
                        "docstring": ast.get_docstring(node),
                        "line": node.lineno,
                        "args": args,
                        "return_type": return_type
                    })
            
            # Generate documentation
            rel_path = os.path.relpath(file_path, ".")
            file_name = os.path.basename(file_path)
            
            doc = f"""# {file_name.replace('.py', '')}

{module_docstring if module_docstring else ''}

## Classes

"""
            
            for cls in classes:
                doc += f"""
### {cls['name']}
{cls['docstring'] if cls['docstring'] else ''}

**Line:** {cls['line']}

"""
            
            doc += "/n## Functions/n/n"
            
            for func in functions:
                doc += f"""
### {func['name']}({', '.join(func['args'])}) -> {func['return_type']}
{func['docstring'] if func['docstring'] else ''}

**Line:** {func['line']}

"""
            
            doc += "/n---/n*Generated by AgentDaf1.1 Tools Manager*/n"
            
            return doc
            
        except Exception as e:
            self.logger.error(f"Documentation generation failed for {file_path}: {str(e)}")
            return f"# Error generating documentation for {file_path}: {str(e)}"
    
    def create_backup(self, source_path: str, backup_dir: str = None) -> Dict[str, Any]:
        """Create backup of specified source.
        
        Args:
            source_path: Path to backup
            backup_dir: Directory to store backup (optional)
            
        Returns:
            Dictionary containing backup results
        """
        try:
            if not os.path.exists(source_path):
                return {
                    "success": False,
                    "error": f"Source path not found: {source_path}",
                    "backup_path": ""
                }
                
            if not backup_dir:
                backup_dir = os.path.join(os.path.dirname(source_path), "backups")
                
            os.makedirs(backup_dir, exist_ok=True)
            
            # Create timestamped backup
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.basename(source_path)
            backup_name = f"{timestamp}_{filename}"
            backup_path = os.path.join(backup_dir, backup_name)
            
            # Copy file
            shutil.copy2(source_path, backup_path)
            
            return {
                "success": True,
                "backup_path": backup_path,
                "timestamp": timestamp,
                "original_path": source_path
            }
            
        except Exception as e:
            self.logger.error(f"Backup creation failed: {str(e)}")
            return {
                "success": False,
                "error": f"Backup creation failed: {str(e)}",
                "backup_path": ""
            }
    
    def deploy_project(self, deployment_type: str = "local") -> Dict[str, Any]:
        """Deploy project using specified deployment type.
        
        Args:
            deployment_type: Type of deployment (local, staging, production)
            
        Returns:
            Dictionary containing deployment results
        """
        try:
            # Check for Docker setup
            docker_compose_files = ['docker-compose.yml', 'docker-compose.production.yml', 'docker-compose.staging.yml']
            
            if any(os.path.exists(f) for f in docker_compose_files):
                # Docker deployment
                compose_file = None
                if deployment_type == "production":
                    if os.path.exists('docker-compose.production.yml'):
                        compose_file = 'docker-compose.production.yml'
                    else:
                        compose_file = 'docker-compose.yml'
                elif deployment_type == "staging":
                    if os.path.exists('docker-compose.staging.yml'):
                        compose_file = 'docker-compose.staging.yml'
                    else:
                        compose_file = 'docker-compose.yml'
                else:
                    compose_file = 'docker-compose.yml'
                
                cmd = ['docker-compose', '-f', compose_file, 'up', '-d']
                
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    cwd=os.getcwd()
                )
                
                return {
                    "success": result.returncode == 0,
                    "deployment_type": deployment_type,
                    "command": ' '.join(cmd),
                    "output": result.stdout.strip() if result.stdout else "",
                    "error": result.stderr.strip() if result.stderr else "",
                    "compose_file": compose_file
                }
            else:
                # Local deployment
                python_cmd = ['python', 'app.py']
                
                # Set environment variables
                env = os.environ.copy()
                env['DEPLOYMENT_MODE'] = deployment_type
                
                result = subprocess.run(
                    python_cmd,
                    capture_output=True,
                    text=True,
                    cwd=os.getcwd(),
                    env=env
                )
                
                return {
                    "success": result.returncode == 0,
                    "deployment_type": deployment_type,
                    "command": ' '.join(python_cmd),
                    "output": result.stdout.strip() if result.stdout else "",
                    "error": result.stderr.strip() if result.stderr else "",
                    "environment": deployment_type
                }
                
        except Exception as e:
            self.logger.error(f"Deployment failed: {str(e)}")
            return {
                "success": False,
                "error": f"Deployment failed: {str(e)}",
                "output": ""
            }
    
    def analyze_performance(self, target: str = None) -> Dict[str, Any]:
        """Analyze performance of specified target.
        
        Args:
            target: Target to analyze (file, directory, or application)
            
        Returns:
            Dictionary containing performance analysis
        """
        try:
            if not target:
                target = "."
                
            analysis = {
                "timestamp": datetime.now().isoformat(),
                "target": target,
                "metrics": {}
            }
            
            if os.path.isfile(target):
                # File analysis
                stat = os.stat(target)
                analysis["metrics"]["file_size"] = stat.st_size
                analysis["metrics"]["last_modified"] = datetime.fromtimestamp(stat.st_mtime).isoformat()
                
                # Simple code complexity analysis
                with open(target, 'r') as f:
                    content = f.read()
                    lines = content.split('/n')
                    analysis["metrics"]["lines_of_code"] = len(lines)
                    analysis["metrics"]["functions"] = content.count('def ')
                    analysis["metrics"]["classes"] = content.count('class ')
                    
            elif os.path.isdir(target):
                # Directory analysis
                files = []
                total_lines = 0
                total_size = 0
                
                for root, dirs, filenames in os.walk(target):
                    for filename in filenames:
                        if filename.endswith('.py'):
                            file_path = os.path.join(root, filename)
                            stat = os.stat(file_path)
                            files.append({
                                "path": file_path,
                                "size": stat.st_size,
                                "lines": self._count_lines(file_path)
                            })
                            total_lines += self._count_lines(file_path)
                            total_size += stat.st_size
                
                analysis["metrics"]["files"] = len(files)
                analysis["metrics"]["total_lines"] = total_lines
                analysis["metrics"]["total_size"] = total_size
                
            return {
                "success": True,
                "analysis": analysis
            }
            
        except Exception as e:
            self.logger.error(f"Performance analysis failed: {str(e)}")
            return {
                "success": False,
                "error": f"Performance analysis failed: {str(e)}",
                "analysis": {}
            }
    
    def _count_lines(self, file_path: str) -> int:
        """Count lines in a Python file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return len(f.read().split('/n'))
        except:
            return 0
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get system information for debugging.
        
        Returns:
            Dictionary containing system information
        """
        try:
            import platform
            import psutil
            
            info = {
                "timestamp": datetime.now().isoformat(),
                "platform": platform.platform(),
                "python_version": platform.python_version(),
                "cpu_count": psutil.cpu_count(),
                "memory_total": psutil.virtual_memory().total,
                "memory_available": psutil.virtual_memory().available,
                "disk_usage": psutil.disk_usage('/'),
                "environment": dict(os.environ)
            }
            
            # Add Git information if available
            try:
                result = subprocess.run(
                    ['git', '--version'],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    info["git_version"] = result.stdout.strip()
            except:
                info["git_version"] = "Not available"
                
            return info
            
        except Exception as e:
            self.logger.error(f"System info collection failed: {str(e)}")
            return {
                "success": False,
                "error": f"System info collection failed: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    def cleanup_temp_files(self, temp_dir: str = None) -> Dict[str, Any]:
        """Clean up temporary files and directories.
        
        Args:
            temp_dir: Temporary directory to clean (optional)
            
        Returns:
            Dictionary containing cleanup results
        """
        try:
            if not temp_dir:
                temp_dir = tempfile.gettempdir()
                
            cleaned_files = []
            cleaned_dirs = []
            
            for item in os.listdir(temp_dir):
                item_path = os.path.join(temp_dir, item)
                
                try:
                    if os.path.isfile(item_path):
                        # Remove temporary files older than 1 hour
                        stat = os.stat(item_path)
                        age_hours = (datetime.now().timestamp() - stat.st_mtime) / 3600
                        
                        if age_hours > 1:
                            os.remove(item_path)
                            cleaned_files.append(item_path)
                    elif os.path.isdir(item_path):
                        # Remove empty temporary directories
                        if not os.listdir(item_path):
                            os.rmdir(item_path)
                            cleaned_dirs.append(item_path)
                            
                except Exception as e:
                    self.logger.warning(f"Failed to clean {item_path}: {str(e)}")
                    
            return {
                "success": True,
                "cleaned_files": len(cleaned_files),
                "cleaned_directories": len(cleaned_dirs),
                "temp_directory": temp_dir
            }
            
        except Exception as e:
            self.logger.error(f"Cleanup failed: {str(e)}")
            return {
                "success": False,
                "error": f"Cleanup failed: {str(e)}",
                "cleaned_files": 0,
                "cleaned_directories": 0
            }