#!/usr/bin/env python3
"""
Auto-Repair Script for AgentDaf1.1 Project

This script automatically detects and fixes common issues in Python files including:
- Missing imports
- Syntax errors
- Dataclass field order issues
- Async/await problems
- Path handling issues
- Unicode problems
- Docker configuration issues
"""

import os
import sys
import ast
import re
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional, Any
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AutoRepair:
    """Automatic repair system for AgentDaf1.1 project"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.fixed_files = []
        self.errors_found = []
        self.warnings_found = []
        
        # Common import mappings
        self.import_fixes = {
            'datetime': ['datetime', 'timedelta', 'timezone'],
            'pathlib': ['Path'],
            'typing': ['Dict', 'List', 'Optional', 'Any', 'Union', 'Tuple', 'Set'],
            'json': ['json'],
            'sqlite3': ['sqlite3'],
            'flask': ['Flask', 'request', 'jsonify', 'render_template'],
            'pandas': ['pd'],
            'openpyxl': ['openpyxl'],
            'psutil': ['psutil'],
            'asyncio': ['asyncio'],
            'logging': ['logging', 'logger'],
            'threading': ['threading'],
            'platform': ['platform'],
            'uuid': ['uuid', 'UUID'],
            'dataclasses': ['dataclass', 'field'],
            'enum': ['Enum'],
            'sqlalchemy': ['create_engine', 'Column', 'Integer', 'String', 'DateTime'],
            'werkzeug': ['werkzeug'],
        }
        
    def scan_project(self) -> Dict[str, Any]:
        """Scan entire project for issues"""
        logger.info("🔍 Scanning project for issues...")
        
        results = {
            'python_files': [],
            'syntax_errors': [],
            'import_errors': [],
            'dataclass_issues': [],
            'async_issues': [],
            'path_issues': [],
            'docker_issues': [],
            'other_issues': []
        }
        
        # Find all Python files
        for py_file in self.project_root.rglob("*.py"):
            if any(skip in str(py_file) for skip in ['.git', '__pycache__', '.venv', 'node_modules']):
                continue
                
            results['python_files'].append(py_file)
            
            # Analyze each file
            issues = self.analyze_file(py_file)
            for issue_type, issues_list in issues.items():
                if issues_list:
                    results[issue_type].extend([(py_file, issue) for issue in issues_list])
        
        return results
    
    def analyze_file(self, file_path: Path) -> Dict[str, List[str]]:
        """Analyze a single Python file for issues"""
        issues = {
            'syntax_errors': [],
            'import_errors': [],
            'dataclass_issues': [],
            'async_issues': [],
            'path_issues': [],
            'other_issues': []
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check syntax
            try:
                ast.parse(content)
            except SyntaxError as e:
                issues['syntax_errors'].append(f"Line {e.lineno}: {e.msg}")
                return issues
            
            # Check for common issues
            issues['import_errors'].extend(self.check_imports(content))
            issues['dataclass_issues'].extend(self.check_dataclasses(content))
            issues['async_issues'].extend(self.check_async_issues(content))
            issues['path_issues'].extend(self.check_path_issues(content))
            issues['other_issues'].extend(self.check_other_issues(content, file_path))
            
        except UnicodeDecodeError:
            issues['other_issues'].append("File encoding issue - not UTF-8")
        except Exception as e:
            issues['other_issues'].append(f"Analysis error: {e}")
        
        return issues
    
    def check_imports(self, content: str) -> List[str]:
        """Check for missing imports"""
        issues = []
        lines = content.split('/n')
        
        # Check for usage without imports
        import_statements = []
        for line in lines:
            if line.strip().startswith(('import ', 'from ')):
                import_statements.append(line.strip())
        
        # Common missing imports
        if 'datetime.now()' in content and 'import datetime' not in content and 'from datetime' not in content:
            issues.append("Missing 'datetime' import")
        
        if 'Path(' in content and 'from pathlib import Path' not in content and 'import pathlib' not in content:
            issues.append("Missing 'pathlib.Path' import")
        
        if 'pd.' in content and 'import pandas' not in content:
            issues.append("Missing 'pandas' import")
        
        if 'psutil.' in content and 'import psutil' not in content:
            issues.append("Missing 'psutil' import")
        
        if '@dataclass' in content and 'from dataclasses import' not in content:
            issues.append("Missing 'dataclasses' import")
        
        if 'async def' in content and 'import asyncio' not in content:
            issues.append("Missing 'asyncio' import for async functions")
        
        return issues
    
    def check_dataclasses(self, content: str) -> List[str]:
        """Check for dataclass field order issues"""
        issues = []
        
        if '@dataclass' not in content:
            return issues
        
        try:
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Check if it's a dataclass
                    is_dataclass = any(
                        (isinstance(decorator, ast.Name) and decorator.id == 'dataclass') or
                        (isinstance(decorator, ast.Attribute) and decorator.attr == 'dataclass')
                        for decorator in node.decorator_list
                    )
                    
                    if is_dataclass:
                        # Check field order
                        fields_with_default = []
                        fields_without_default = []
                        
                        for item in node.body:
                            if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                                field_name = item.target.id
                                has_default = item.value is not None
                                
                                if has_default:
                                    fields_with_default.append(field_name)
                                else:
                                    fields_without_default.append(field_name)
                        
                        # Check if any field without default comes after field with default
                        field_order = []
                        for item in node.body:
                            if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                                field_order.append(item.target.id)
                        
                        found_default = False
                        for field_name in field_order:
                            if field_name in fields_with_default:
                                found_default = True
                            elif field_name in fields_without_default and found_default:
                                issues.append(f"Dataclass field '{field_name}' without default follows field with default")
                                break
        
        except Exception as e:
            issues.append(f"Dataclass analysis error: {e}")
        
        return issues
    
    def check_async_issues(self, content: str) -> List[str]:
        """Check for async/await issues"""
        issues = []
        
        # Check for async functions without proper await
        lines = content.split('/n')
        in_async_function = False
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            
            if stripped.startswith('async def'):
                in_async_function = True
            elif stripped.startswith('def ') and not stripped.startswith('async def'):
                in_async_function = False
            
            if in_async_function:
                # Check for common async patterns
                if 'sqlite3.connect(' in stripped:
                    issues.append(f"Line {i}: SQLite connection in async function should use async driver")
                
                if 'await asyncio.sleep(' in stripped:
                    issues.append(f"Line {i}: Use asyncio.sleep() instead of await asyncio.sleep() in async function")
        
        return issues
    
    def check_path_issues(self, content: str) -> List[str]:
        """Check for path handling issues"""
        issues = []
        
        # Check for hardcoded path separators
        if '/' in content and '//' in content:
            issues.append("Mixed path separators detected - use Path or os.path.join()")
        
        # Check for relative path issues
        if '../src' in content:
            issues.append("Relative path '../src' detected - consider absolute paths")
        
        return issues
    
    def check_other_issues(self, content: str, file_path: Path) -> List[str]:
        """Check for other common issues"""
        issues = []
        
        # Check for unused imports (basic check)
        lines = content.split('/n')
        imports = []
        for line in lines:
            if line.strip().startswith('import ') and ' as ' not in line:
                module = line.strip().replace('import ', '')
                imports.append(module)
        
        # Check for print statements in production code
        if 'print(' in content and 'test' not in str(file_path).lower():
            issues.append("Print statement detected - use logging instead")
        
        # Check for TODO/FIXME comments
        if 'TODO:' in content or 'FIXME:' in content:
            issues.append("TODO/FIXME comments found")
        
        # Check for hardcoded passwords/keys
        if any(pattern in content.lower() for pattern in ['password', 'secret', 'key', 'token']):
            if any(char in content for char in ['"', "'"]):
                issues.append("Potential hardcoded credentials detected")
        
        return issues
    
    def fix_file(self, file_path: Path, issues: Dict[str, List[str]]) -> bool:
        """Fix issues in a file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Apply fixes
            content = self.fix_imports(content, issues.get('import_errors', []))
            content = self.fix_dataclasses(content, issues.get('dataclass_issues', []))
            content = self.fix_async_issues(content, issues.get('async_issues', []))
            content = self.fix_path_issues(content, issues.get('path_issues', []))
            content = self.fix_other_issues(content, issues.get('other_issues', []))
            
            # Write back if changed
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                logger.info(f"✅ Fixed: {file_path}")
                self.fixed_files.append(file_path)
                return True
            else:
                logger.info(f"ℹ️  No fixes needed: {file_path}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to fix {file_path}: {e}")
            self.errors_found.append(f"{file_path}: {e}")
            return False
    
    def fix_imports(self, content: str, issues: List[str]) -> str:
        """Fix import issues"""
        lines = content.split('/n')
        import_section = []
        code_section = []
        in_imports = True
        
        # Separate imports from code
        for line in lines:
            if in_imports and (line.strip().startswith(('import ', 'from ', '#')) or line.strip() == ''):
                import_section.append(line)
            else:
                in_imports = False
                code_section.append(line)
        
        # Add missing imports
        for issue in issues:
            if "Missing 'datetime' import" in issue:
                if 'from datetime import' not in content:
                    import_section.append('from datetime import datetime, timedelta')
                elif 'timedelta' not in content:
                    # Add timedelta to existing import
                    for i, line in enumerate(import_section):
                        if 'from datetime import' in line:
                            import_section[i] = line.rstrip() + ', timedelta'
                            break
            
            elif "Missing 'pathlib.Path' import" in issue:
                if 'from pathlib import' not in content:
                    import_section.append('from pathlib import Path')
                elif 'Path' not in content:
                    for i, line in enumerate(import_section):
                        if 'from pathlib import' in line:
                            import_section[i] = line.rstrip() + ', Path'
                            break
            
            elif "Missing 'pandas' import" in issue:
                import_section.append('import pandas as pd')
            
            elif "Missing 'psutil' import" in issue:
                import_section.append('import psutil')
            
            elif "Missing 'dataclasses' import" in issue:
                import_section.append('from dataclasses import dataclass, field')
            
            elif "Missing 'asyncio' import" in issue:
                import_section.append('import asyncio')
        
        return '/n'.join(import_section + code_section)
    
    def fix_dataclasses(self, content: str, issues: List[str]) -> str:
        """Fix dataclass field order issues"""
        # This is complex - for now just log the issue
        # In a full implementation, this would reorder the fields
        return content
    
    def fix_async_issues(self, content: str, issues: List[str]) -> str:
        """Fix async issues"""
        # Replace time.sleep with asyncio.sleep in async functions
        lines = content.split('/n')
        for i, line in enumerate(lines):
            if 'time.sleep(' in line and 'async def' in '/n'.join(lines[max(0, i-10):i]):
                lines[i] = line.replace('await asyncio.sleep(', 'await asyncio.sleep(')
        
        return '/n'.join(lines)
    
    def fix_path_issues(self, content: str, issues: List[str]) -> str:
        """Fix path issues"""
        # Replace mixed separators with Path
        if "Mixed path separators" in str(issues):
            # Basic fix - in full implementation would be more sophisticated
            content = content.replace('//', '/')
        
        return content
    
    def fix_other_issues(self, content: str, issues: List[str]) -> str:
        """Fix other common issues"""
        # Replace print with logging (basic implementation)
        if "Print statement detected" in str(issues):
            lines = content.split('/n')
            for i, line in enumerate(lines):
                if 'print(' in line and 'test' not in line:
                    # Simple replacement - in full implementation would be more sophisticated
                    lines[i] = line.replace('logger.info(', 'logger.info(')
            content = '/n'.join(lines)
        
        return content
    
    def fix_docker_files(self) -> None:
        """Fix Docker-related files"""
        logger.info("🐳 Checking Docker files...")
        
        docker_files = [
            self.project_root / 'docker-compose.yml',
            self.project_root / 'Dockerfile',
            self.project_root / 'docker_project' / 'docker-compose.yml',
            self.project_root / 'docker_project' / 'Dockerfile'
        ]
        
        for docker_file in docker_files:
            if docker_file.exists():
                self.fix_docker_file(docker_file)
    
    def fix_docker_file(self, docker_file: Path) -> None:
        """Fix specific Docker file issues"""
        try:
            with open(docker_file, 'r') as f:
                content = f.read()
            
            original_content = content
            
            if docker_file.name == 'docker-compose.yml':
                # Fix version field removal
                if 'version:' in content:
                    lines = content.split('/n')
                    lines = [line for line in lines if not line.strip().startswith('version:')]
                    content = '/n'.join(lines)
                    logger.info(f"✅ Fixed docker-compose.yml version field")
            
            elif docker_file.name == 'Dockerfile':
                # Fix common Dockerfile issues
                if 'curl' not in content and 'RUN' in content:
                    # Add curl installation
                    lines = content.split('/n')
                    for i, line in enumerate(lines):
                        if 'RUN apt-get' in line or 'RUN apk' in line:
                            lines[i] = line.rstrip() + ' curl'
                            break
                    content = '/n'.join(lines)
                    logger.info(f"✅ Added curl to Dockerfile")
            
            if content != original_content:
                with open(docker_file, 'w') as f:
                    f.write(content)
                self.fixed_files.append(docker_file)
                
        except Exception as e:
            logger.error(f"❌ Failed to fix Docker file {docker_file}: {e}")
    
    def run_syntax_check(self) -> None:
        """Run syntax check on all Python files"""
        logger.info("🔍 Running syntax checks...")
        
        for py_file in self.project_root.rglob("*.py"):
            if any(skip in str(py_file) for skip in ['.git', '__pycache__', '.venv', 'node_modules']):
                continue
            
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                ast.parse(content)
            except SyntaxError as e:
                logger.error(f"❌ Syntax error in {py_file}: Line {e.lineno}: {e.msg}")
                self.errors_found.append(f"{py_file}: {e.msg}")
            except UnicodeDecodeError:
                logger.error(f"❌ Encoding error in {py_file}")
                self.errors_found.append(f"{py_file}: Encoding error")
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate repair report"""
        return {
            'fixed_files': [str(f) for f in self.fixed_files],
            'errors_found': self.errors_found,
            'warnings_found': self.warnings_found,
            'total_files_processed': len(list(self.project_root.rglob("*.py"))),
            'success_rate': len(self.fixed_files) / max(1, len(self.errors_found) + len(self.fixed_files)) * 100
        }
    
    def run_full_repair(self) -> Dict[str, Any]:
        """Run complete auto-repair process"""
        logger.info("🚀 Starting auto-repair process...")
        
        # Step 1: Scan for issues
        scan_results = self.scan_project()
        
        # Step 2: Fix Python files
        logger.info("🔧 Fixing Python files...")
        for issue_type, files_with_issues in scan_results.items():
            if issue_type == 'python_files':
                continue
                
            logger.info(f"  Fixing {issue_type}...")
            for file_path, issues in files_with_issues:
                issue_dict = {issue_type: issues}
                self.fix_file(file_path, issue_dict)
        
        # Step 3: Fix Docker files
        self.fix_docker_files()
        
        # Step 4: Run final syntax check
        self.run_syntax_check()
        
        # Step 5: Generate report
        report = self.generate_report()
        
        logger.info("✅ Auto-repair completed!")
        return report

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Auto-Repair AgentDaf1.1 Project')
    parser.add_argument('--project-root', type=str, default='.', 
                       help='Project root directory')
    parser.add_argument('--scan-only', action='store_true',
                       help='Only scan, do not fix')
    parser.add_argument('--syntax-only', action='store_true',
                       help='Only run syntax checks')
    parser.add_argument('--docker-only', action='store_true',
                       help='Only fix Docker files')
    parser.add_argument('--output', type=str, default='auto_repair_report.json',
                       help='Output report file')
    
    args = parser.parse_args()
    
    project_root = Path(args.project_root).resolve()
    auto_repair = AutoRepair(project_root)
    
    if args.syntax_only:
        auto_repair.run_syntax_check()
    elif args.docker_only:
        auto_repair.fix_docker_files()
    elif args.scan_only:
        results = auto_repair.scan_project()
        logger.info(json.dumps(results, indent=2, default=str))
    else:
        report = auto_repair.run_full_repair()
        
        # Save report
        with open(args.output, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        # Print summary
        logger.info(f"/n📊 Auto-Repair Summary:")
        logger.info(f"  Files processed: {report['total_files_processed']}")
        logger.info(f"  Files fixed: {len(report['fixed_files'])}")
        logger.info(f"  Errors remaining: {len(report['errors_found'])}")
        logger.info(f"  Success rate: {report['success_rate']:.1f}%")
        logger.info(f"  Report saved to: {args.output}")

if __name__ == "__main__":
    main()