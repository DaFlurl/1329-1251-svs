#!/usr/bin/env python3
"""
Comprehensive Error Detection and Auto-Fix Tool
Detects and fixes common Python errors, import issues, and syntax problems
"""

import os
import ast
import re
import sys
import subprocess
import importlib.util
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import json

class ErrorDetector:
    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.errors = []
        self.fixes_applied = []
        
    def scan_all_python_files(self) -> List[Path]:
        """Find all Python files in the project"""
        python_files = []
        for root, dirs, files in os.walk(self.project_root):
            # Skip hidden directories and common cache dirs
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules', '.git']]
            
            for file in files:
                if file.endswith('.py'):
                    python_files.append(Path(root) / file)
        return python_files
    
    def check_syntax_errors(self, file_path: Path) -> List[Dict]:
        """Check for syntax errors in a Python file"""
        errors = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            ast.parse(content)
        except SyntaxError as e:
            errors.append({
                'type': 'syntax_error',
                'file': str(file_path),
                'line': e.lineno or 0,
                'column': e.offset or 0,
                'message': str(e),
                'severity': 'critical'
            })
        except UnicodeDecodeError as e:
            errors.append({
                'type': 'encoding_error',
                'file': str(file_path),
                'message': f'Encoding error: {str(e)}',
                'severity': 'high'
            })
        except Exception as e:
            errors.append({
                'type': 'parse_error',
                'file': str(file_path),
                'message': f'Parse error: {str(e)}',
                'severity': 'high'
            })
        return errors
    
    def check_import_errors(self, file_path: Path) -> List[Dict]:
        """Check for import errors and missing modules"""
        errors = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        module_name = alias.name
                        if not self.is_module_available(module_name):
                            errors.append({
                                'type': 'missing_module',
                                'file': str(file_path),
                                'line': node.lineno,
                                'module': module_name,
                                'message': f'Missing module: {module_name}',
                                'severity': 'high'
                            })
                
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        module_name = node.module
                        if not self.is_module_available(module_name):
                            errors.append({
                                'type': 'missing_module',
                                'file': str(file_path),
                                'line': node.lineno,
                                'module': module_name,
                                'message': f'Missing module: {module_name}',
                                'severity': 'high'
                            })
        
        except Exception as e:
            # If we can't parse the file, syntax errors will catch this
            pass
        
        return errors
    
    def is_module_available(self, module_name: str) -> bool:
        """Check if a module is available for import"""
        try:
            # Handle relative imports and built-in modules
            if module_name.startswith('.'):
                return True
            
            # Check standard library and installed packages
            spec = importlib.util.find_spec(module_name)
            return spec is not None
        except (ImportError, ModuleNotFoundError, ValueError):
            return False
    
    def check_common_issues(self, file_path: Path) -> List[Dict]:
        """Check for common Python code issues"""
        errors = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for i, line in enumerate(lines, 1):
                # Check for print statements (should use logging)
                if 'logger.info(' in line and not line.strip().startswith('#'):
                    errors.append({
                        'type': 'print_statement',
                        'file': str(file_path),
                        'line': i,
                        'message': 'Consider using logging instead of logger.info()',
                        'severity': 'info'
                    })
                
                # Check for TODO/FIXME comments
                if re.search(r'#/s*(TODO|FIXME|XXX)', line, re.IGNORECASE):
                    errors.append({
                        'type': 'todo_comment',
                        'file': str(file_path),
                        'line': i,
                        'message': 'TODO/FIXME comment found',
                        'severity': 'info'
                    })
                
                # Check for bare except clauses
                if re.search(r'except/s*:', line):
                    errors.append({
                        'type': 'bare_except',
                        'file': str(file_path),
                        'line': i,
                        'message': 'Bare except clause - specify exception type',
                        'severity': 'medium'
                    })
        
        except Exception:
            pass
        
        return errors
    
    def fix_encoding_errors(self, file_path: Path) -> bool:
        """Fix encoding errors by converting to UTF-8"""
        try:
            # Try to read with different encodings
            encodings = ['utf-8', 'latin-1', 'cp1252']
            content = None
            encoding_used = None
            
            for enc in encodings:
                try:
                    with open(file_path, 'r', encoding=enc) as f:
                        content = f.read()
                    encoding_used = enc
                    break
                except UnicodeDecodeError:
                    continue
            
            if content and encoding_used != 'utf-8':
                # Write back as UTF-8
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.fixes_applied.append(f'Fixed encoding in {file_path} ({encoding_used} -> utf-8)')
                return True
        
        except Exception as e:
            logger.info(f"Could not fix encoding in {file_path}: {e}")
        
        return False
    
    def auto_fix_syntax_errors(self, file_path: Path) -> bool:
        """Attempt to auto-fix common syntax errors"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Fix common syntax issues
            # 1. Fix missing colons in if/for/while/def/class statements
            content = re.sub(r'^(/s*(if|for|while|def|class|elif|else|try|except|finally)/s.+[^/s:])/s*$', 
                           r'/1:', content, flags=re.MULTILINE)
            
            # 2. Fix missing parentheses in print statements (Python 2 style)
            content = re.sub(r'^(/s*)print/s+(.+)$', 
                           r'/1logger.info(/2)', content, flags=re.MULTILINE)
            
            # 3. Fix trailing commas in function definitions
            content = re.sub(r'def/s+(/w+)/s*/([^,)]+,/s*/)', 
                           r'def /1(/1)', content)
            
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.fixes_applied.append(f'Auto-fixed syntax errors in {file_path}')
                return True
        
        except Exception as e:
            logger.info(f"Could not auto-fix syntax in {file_path}: {e}")
        
        return False
    
    def run_comprehensive_scan(self) -> Dict:
        """Run comprehensive error detection and fixing"""
        logger.info("Starting comprehensive error detection...")
        
        python_files = self.scan_all_python_files()
        logger.info(f"Found {len(python_files)} Python files")
        
        total_errors = 0
        critical_errors = 0
        files_with_errors = 0
        
        for file_path in python_files:
            file_errors = []
            
            # Check syntax errors first
            syntax_errors = self.check_syntax_errors(file_path)
            if syntax_errors:
                # Try to fix encoding errors first
                self.fix_encoding_errors(file_path)
                # Try to auto-fix syntax errors
                self.auto_fix_syntax_errors(file_path)
                # Re-check syntax
                syntax_errors = self.check_syntax_errors(file_path)
            
            file_errors.extend(syntax_errors)
            file_errors.extend(self.check_import_errors(file_path))
            file_errors.extend(self.check_common_issues(file_path))
            
            if file_errors:
                files_with_errors += 1
                for error in file_errors:
                    self.errors.append(error)
                    total_errors += 1
                    if error['severity'] == 'critical':
                        critical_errors += 1
        
        return {
            'total_files': len(python_files),
            'files_with_errors': files_with_errors,
            'total_errors': total_errors,
            'critical_errors': critical_errors,
            'fixes_applied': len(self.fixes_applied)
        }
    
    def generate_report(self) -> str:
        """Generate detailed error report"""
        report = []
        report.append("=" * 60)
        report.append("🔍 COMPREHENSIVE ERROR DETECTION REPORT")
        report.append("=" * 60)
        
        # Summary by severity
        severity_counts = {}
        error_types = {}
        
        for error in self.errors:
            severity = error['severity']
            error_type = error['type']
            
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
            error_types[error_type] = error_types.get(error_type, 0) + 1
        
        report.append(f"/n📊 ERROR SUMMARY:")
        report.append(f"   Total Errors: {len(self.errors)}")
        
        for severity in ['critical', 'high', 'medium', 'info']:
            count = severity_counts.get(severity, 0)
            if count > 0:
                icon = {'critical': '🚨', 'high': '⚠️', 'medium': '⚡', 'info': 'ℹ️'}[severity]
                report.append(f"   {icon} {severity.capitalize()}: {count}")
        
        report.append(f"/n🔧 FIXES APPLIED: {len(self.fixes_applied)}")
        
        if self.fixes_applied:
            report.append("/nApplied fixes:")
            for fix in self.fixes_applied:
                report.append(f"  ✅ {fix}")
        
        # Error details by type
        if error_types:
            report.append(f"/n📋 ERRORS BY TYPE:")
            for error_type, count in sorted(error_types.items()):
                report.append(f"   {error_type}: {count}")
        
        # Critical errors first
        critical_errors = [e for e in self.errors if e['severity'] == 'critical']
        if critical_errors:
            report.append(f"/n🚨 CRITICAL ERRORS (require immediate attention):")
            for error in critical_errors[:10]:  # Limit to first 10
                report.append(f"   ❌ {error['file']}:{error.get('line', '?')} - {error['message']}")
        
        # High priority errors
        high_errors = [e for e in self.errors if e['severity'] == 'high']
        if high_errors:
            report.append(f"/n⚠️ HIGH PRIORITY ERRORS:")
            for error in high_errors[:10]:  # Limit to first 10
                report.append(f"   ⚠️ {error['file']}:{error.get('line', '?')} - {error['message']}")
        
        report.append("/n" + "=" * 60)
        
        return "/n".join(report)
    
    def save_report(self, filename: str = "error_report.json"):
        """Save detailed error data to JSON file"""
        report_data = {
            'scan_time': str(Path.cwd()),
            'total_errors': len(self.errors),
            'errors': self.errors,
            'fixes_applied': self.fixes_applied
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, default=str)
        
        logger.info(f"📄 Detailed report saved to {filename}")

def main():
    """Main function to run the error detector"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Comprehensive Python Error Detection and Auto-Fix Tool')
    parser.add_argument('--path', '-p', default='.', help='Project path to scan (default: current directory)')
    parser.add_argument('--fix', '-f', action='store_true', help='Apply auto-fixes when possible')
    parser.add_argument('--save', '-s', action='store_true', help='Save detailed report to JSON')
    parser.add_argument('--quiet', '-q', action='store_true', help='Minimal output')
    
    args = parser.parse_args()
    
    detector = ErrorDetector(args.path)
    
    # Run comprehensive scan
    results = detector.run_comprehensive_scan()
    
    if not args.quiet:
        # Generate and print report
        report = detector.generate_report()
        logger.info(report)
        
        # Summary
        if results['critical_errors'] == 0:
            logger.info("🎉 No critical errors found!")
        else:
            logger.info(f"🚨 {results['critical_errors']} critical errors require immediate attention!")
        
        if results['fixes_applied'] > 0:
            logger.info(f"🔧 Applied {results['fixes_applied']} automatic fixes")
    
    # Save detailed report if requested
    if args.save:
        detector.save_report()
    
    # Exit with appropriate code
    sys.exit(0 if results['critical_errors'] == 0 else 1)

if __name__ == "__main__":
    main()