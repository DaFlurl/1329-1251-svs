#!/usr/bin/env python3
"""
AgentDaf1.1 - Code Analyzer Tool
Code quality, complexity analysis, and security scanning
"""

import json
import time
import ast
import os
import re
import subprocess
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
import logging
import sqlite3
import hashlib

class CodeAnalyzer:
    """Code quality, complexity analysis, and security scanning"""
    
    def __init__(self):
        self.name = "Code Analyzer"
        self.version = "1.0.0"
        self.logger = logging.getLogger(__name__)
        self.lock = threading.Lock() if 'threading' in globals() else None
        
        # Project paths
        self.project_root = Path(__file__).parent.parent.parent.parent
        self.analysis_db_path = self.project_root / "data" / "code_analysis.db"
        
        # Ensure data directory exists
        self.analysis_db_path.parent.mkdir(exist_ok=True)
        
        # Analysis configuration
        self.config = {
            "max_complexity": 10,
            "max_function_length": 50,
            "max_class_length": 200,
            "security_scan_enabled": True,
            "style_check_enabled": True,
            "test_coverage_threshold": 80,
            "supported_extensions": [".py", ".js", ".ts", ".java", ".cpp", ".c"],
            "ignore_patterns": ["__pycache__", ".git", "node_modules", ".venv", "venv"]
        }
        
        # Security patterns
        self.security_patterns = {
            "sql_injection": [
                r"execute\s*\(\s*['\"].*['\"]",
                r"query\s*=\s*['\"].*['\"]",
                r"cursor\.execute\s*\(\s*.*\+.*\)"
            ],
            "hardcoded_secrets": [
                r"password\s*=\s*['\"][^'\"]{8,}['\"]",
                r"api_key\s*=\s*['\"][^'\"]{16,}['\"]",
                r"secret\s*=\s*['\"][^'\"]{16,}['\"]",
                r"token\s*=\s*['\"][^'\"]{16,}['\"]"
            ],
            "insecure_crypto": [
                r"md5/s*/(",
                r"sha1/s*/(",
                r"DES/s*/(",
                r"RC4/s*/("
            ],
            "command_injection": [
                r"os/.system/s*/(",
                r"subprocess/.call/s*/(/s*.*/+.*/)",
                r"eval/s*/(",
                r"exec/s*/("
            ]
        }
        
        # Initialize analysis database
        self._init_analysis_db()
        
        self.logger.info(f"Code Analyzer initialized: {self.name} v{self.version}")
    
    def _init_analysis_db(self):
        """Initialize code analysis database"""
        conn = sqlite3.connect(str(self.analysis_db_path))
        conn.execute('''
            CREATE TABLE IF NOT EXISTS analysis_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT NOT NULL,
                analysis_type TEXT NOT NULL,
                results TEXT NOT NULL,
                metrics TEXT,
                timestamp REAL,
                file_hash TEXT
            )
        ''')
        
        conn.execute('''
            CREATE TABLE IF NOT EXISTS code_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT NOT NULL,
                complexity INTEGER,
                lines_of_code INTEGER,
                functions INTEGER,
                classes INTEGER,
                security_issues INTEGER,
                style_violations INTEGER,
                timestamp REAL
            )
        ''')
        
        conn.execute('''
            CREATE INDEX IF NOT EXISTS idx_file_path ON analysis_results(file_path)
        ''')
        
        conn.execute('''
            CREATE INDEX IF NOT EXISTS idx_timestamp ON analysis_results(timestamp)
        ''')
        
        conn.commit()
        conn.close()
    
    def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """Analyze a single file"""
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                return {"success": False, "error": "File not found"}
            
            if file_path.suffix not in self.config["supported_extensions"]:
                return {"success": False, "error": "Unsupported file type"}
            
            # Calculate file hash
            file_hash = self._calculate_file_hash(file_path)
            
            # Read file content
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Perform different types of analysis
            results = {
                "file_path": str(file_path),
                "file_size": file_path.stat().st_size,
                "file_hash": file_hash,
                "timestamp": datetime.now().isoformat()
            }
            
            # Language-specific analysis
            if file_path.suffix == ".py":
                results.update(self._analyze_python(content, file_path))
            else:
                results.update(self._analyze_generic(content, file_path))
            
            # Security scan
            if self.config["security_scan_enabled"]:
                results["security_analysis"] = self._security_scan(content, file_path)
            
            # Style check
            if self.config["style_check_enabled"]:
                results["style_analysis"] = self._style_check(content, file_path)
            
            # Calculate overall metrics
            results["metrics"] = self._calculate_metrics(results)
            
            # Save to database
            self._save_analysis_results(str(file_path), results, file_hash)
            
            return {"success": True, "results": results}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def analyze_directory(self, directory_path: str, recursive: bool = True) -> Dict[str, Any]:
        """Analyze all files in a directory"""
        try:
            directory_path = Path(directory_path)
            
            if not directory_path.exists():
                return {"success": False, "error": "Directory not found"}
            
            # Find all files to analyze
            files_to_analyze = []
            
            if recursive:
                for file_path in directory_path.rglob("*"):
                    if (file_path.is_file() and 
                        file_path.suffix in self.config["supported_extensions"] and
                        not any(pattern in str(file_path) for pattern in self.config["ignore_patterns"])):
                        files_to_analyze.append(file_path)
            else:
                for file_path in directory_path.iterdir():
                    if (file_path.is_file() and 
                        file_path.suffix in self.config["supported_extensions"]):
                        files_to_analyze.append(file_path)
            
            # Analyze all files
            all_results = []
            errors = []
            
            for file_path in files_to_analyze:
                result = self.analyze_file(str(file_path))
                if result["success"]:
                    all_results.append(result["results"])
                else:
                    errors.append(f"{file_path}: {result['error']}")
            
            # Calculate aggregate metrics
            aggregate_metrics = self._calculate_aggregate_metrics(all_results)
            
            return {
                "success": True,
                "directory": str(directory_path),
                "files_analyzed": len(all_results),
                "files_with_errors": len(errors),
                "results": all_results,
                "aggregate_metrics": aggregate_metrics,
                "errors": errors
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _analyze_python(self, content: str, file_path: Path) -> Dict[str, Any]:
        """Analyze Python code"""
        try:
            tree = ast.parse(content)
            
            analysis = {
                "language": "python",
                "complexity_analysis": self._analyze_complexity(tree),
                "structure_analysis": self._analyze_structure(tree),
                "dependencies": self._analyze_dependencies(tree)
            }
            
            return analysis
            
        except SyntaxError as e:
            return {
                "language": "python",
                "syntax_error": {
                    "line": e.lineno,
                    "column": e.offset,
                    "message": str(e)
                }
            }
    
    def _analyze_generic(self, content: str, file_path: Path) -> Dict[str, Any]:
        """Analyze generic code files"""
        lines = content.split('/n')
        
        analysis = {
            "language": file_path.suffix[1:],  # Remove the dot
            "basic_metrics": {
                "lines_total": len(lines),
                "lines_code": len([line for line in lines if line.strip() and not line.strip().startswith('//') and not line.strip().startswith('#')]),
                "lines_comments": len([line for line in lines if line.strip().startswith('//') or line.strip().startswith('#')]),
                "lines_blank": len([line for line in lines if not line.strip()])
            }
        }
        
        return analysis
    
    def _analyze_complexity(self, tree: ast.AST) -> Dict[str, Any]:
        """Analyze cyclomatic complexity"""
        complexity_visitor = ComplexityVisitor()
        complexity_visitor.visit(tree)
        
        return {
            "total_complexity": complexity_visitor.total_complexity,
            "max_function_complexity": complexity_visitor.max_function_complexity,
            "complex_functions": complexity_visitor.complex_functions,
            "average_complexity": complexity_visitor.average_complexity
        }
    
    def _analyze_structure(self, tree: ast.AST) -> Dict[str, Any]:
        """Analyze code structure"""
        structure_visitor = StructureVisitor()
        structure_visitor.visit(tree)
        
        return {
            "functions": structure_visitor.functions,
            "classes": structure_visitor.classes,
            "imports": structure_visitor.imports,
            "function_count": len(structure_visitor.functions),
            "class_count": len(structure_visitor.classes)
        }
    
    def _analyze_dependencies(self, tree: ast.AST) -> List[str]:
        """Analyze import dependencies"""
        dependencies = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    dependencies.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    dependencies.append(node.module)
        
        return list(set(dependencies))
    
    def _security_scan(self, content: str, file_path: Path) -> Dict[str, Any]:
        """Perform security vulnerability scan"""
        security_issues = []
        
        for category, patterns in self.security_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
                for match in matches:
                    line_num = content[:match.start()].count('/n') + 1
                    line_content = content.split('/n')[line_num - 1].strip()
                    
                    security_issues.append({
                        "category": category,
                        "severity": self._get_severity(category),
                        "line": line_num,
                        "column": match.start() - content.rfind('/n', 0, match.start()) - 1,
                        "pattern": pattern,
                        "matched_text": match.group(),
                        "line_content": line_content
                    })
        
        return {
            "issues_found": len(security_issues),
            "issues": security_issues,
            "severity_summary": self._calculate_severity_summary(security_issues)
        }
    
    def _style_check(self, content: str, file_path: Path) -> Dict[str, Any]:
        """Perform code style checking"""
        style_violations = []
        
        # Basic style checks
        lines = content.split('/n')
        
        for i, line in enumerate(lines, 1):
            # Check line length
            if len(line) > 120:
                style_violations.append({
                    "type": "line_too_long",
                    "line": i,
                    "message": f"Line too long ({len(line)} > 120 characters)"
                })
            
            # Check for trailing whitespace
            if line.rstrip() != line:
                style_violations.append({
                    "type": "trailing_whitespace",
                    "line": i,
                    "message": "Trailing whitespace"
                })
            
            # Check for tabs
            if '/t' in line:
                style_violations.append({
                    "type": "tab_character",
                    "line": i,
                    "message": "Tab character found"
                })
        
        # Python-specific style checks
        if file_path.suffix == ".py":
            try:
                import flake8
                # Run flake8 if available
                result = subprocess.run(
                    ['flake8', '--format=json', str(file_path)],
                    capture_output=True,
                    text=True
                )
                
                if result.stdout:
                    flake8_issues = json.loads(result.stdout)
                    style_violations.extend(flake8_issues)
            except ImportError:
                pass  # flake8 not available
        
        return {
            "violations_found": len(style_violations),
            "violations": style_violations
        }
    
    def _calculate_metrics(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate overall code metrics"""
        metrics = {
            "complexity_score": 0,
            "quality_score": 0,
            "security_score": 0,
            "maintainability_score": 0
        }
        
        # Complexity score
        if "complexity_analysis" in results:
            complexity = results["complexity_analysis"]
            max_complexity = complexity.get("max_function_complexity", 0)
            metrics["complexity_score"] = max(0, 100 - (max_complexity * 5))
        
        # Security score
        if "security_analysis" in results:
            security = results["security_analysis"]
            issues = security.get("issues_found", 0)
            metrics["security_score"] = max(0, 100 - (issues * 10))
        
        # Style/Quality score
        if "style_analysis" in results:
            style = results["style_analysis"]
            violations = style.get("violations_found", 0)
            metrics["quality_score"] = max(0, 100 - (violations * 2))
        
        # Overall maintainability
        metrics["maintainability_score"] = (
            metrics["complexity_score"] * 0.4 +
            metrics["security_score"] * 0.3 +
            metrics["quality_score"] * 0.3
        )
        
        return metrics
    
    def _calculate_aggregate_metrics(self, all_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate aggregate metrics for multiple files"""
        if not all_results:
            return {}
        
        total_files = len(all_results)
        total_complexity = sum(r.get("metrics", {}).get("complexity_score", 0) for r in all_results)
        total_security = sum(r.get("metrics", {}).get("security_score", 0) for r in all_results)
        total_quality = sum(r.get("metrics", {}).get("quality_score", 0) for r in all_results)
        total_maintainability = sum(r.get("metrics", {}).get("maintainability_score", 0) for r in all_results)
        
        security_issues = sum(r.get("security_analysis", {}).get("issues_found", 0) for r in all_results)
        style_violations = sum(r.get("style_analysis", {}).get("violations_found", 0) for r in all_results)
        
        return {
            "total_files": total_files,
            "average_complexity_score": total_complexity / total_files,
            "average_security_score": total_security / total_files,
            "average_quality_score": total_quality / total_files,
            "average_maintainability_score": total_maintainability / total_files,
            "total_security_issues": security_issues,
            "total_style_violations": style_violations,
            "files_with_security_issues": sum(1 for r in all_results if r.get("security_analysis", {}).get("issues_found", 0) > 0),
            "files_with_style_violations": sum(1 for r in all_results if r.get("style_analysis", {}).get("violations_found", 0) > 0)
        }
    
    def _get_severity(self, category: str) -> str:
        """Get severity level for security category"""
        severity_map = {
            "sql_injection": "HIGH",
            "hardcoded_secrets": "HIGH",
            "insecure_crypto": "MEDIUM",
            "command_injection": "HIGH"
        }
        return severity_map.get(category, "LOW")
    
    def _calculate_severity_summary(self, issues: List[Dict[str, Any]]) -> Dict[str, int]:
        """Calculate severity summary"""
        summary = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
        for issue in issues:
            severity = issue.get("severity", "LOW")
            summary[severity] = summary.get(severity, 0) + 1
        return summary
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of file"""
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    
    def _save_analysis_results(self, file_path: str, results: Dict[str, Any], file_hash: str):
        """Save analysis results to database"""
        conn = sqlite3.connect(str(self.analysis_db_path))
        
        # Save full analysis results
        conn.execute('''
            INSERT INTO analysis_results 
            (file_path, analysis_type, results, timestamp, file_hash)
            VALUES (?, ?, ?, ?, ?)
        ''', (file_path, "full", json.dumps(results), time.time(), file_hash))
        
        # Save metrics
        metrics = results.get("metrics", {})
        security_analysis = results.get("security_analysis", {})
        style_analysis = results.get("style_analysis", {})
        
        conn.execute('''
            INSERT INTO code_metrics 
            (file_path, complexity, lines_of_code, functions, classes, security_issues, style_violations, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            file_path,
            metrics.get("complexity_score", 0),
            results.get("basic_metrics", {}).get("lines_code", 0),
            results.get("structure_analysis", {}).get("function_count", 0),
            results.get("structure_analysis", {}).get("class_count", 0),
            security_analysis.get("issues_found", 0),
            style_analysis.get("violations_found", 0),
            time.time()
        ))
        
        conn.commit()
        conn.close()
    
    def get_analysis_history(self, file_path: str = None, limit: int = 50) -> Dict[str, Any]:
        """Get analysis history"""
        conn = sqlite3.connect(str(self.analysis_db_path))
        cursor = conn.cursor()
        
        if file_path:
            cursor.execute('''
                SELECT * FROM analysis_results 
                WHERE file_path = ? 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (file_path, limit))
        else:
            cursor.execute('''
                SELECT * FROM analysis_results 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (limit,))
        
        columns = [desc[0] for desc in cursor.description]
        history = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        
        return {
            "success": True,
            "history": history,
            "total": len(history)
        }
    
    def get_code_metrics(self, limit: int = 100) -> Dict[str, Any]:
        """Get code metrics summary"""
        conn = sqlite3.connect(str(self.analysis_db_path))
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM code_metrics 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (limit,))
        
        columns = [desc[0] for desc in cursor.description]
        metrics = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        # Calculate aggregates
        if metrics:
            avg_complexity = sum(m["complexity"] for m in metrics) / len(metrics)
            avg_security_issues = sum(m["security_issues"] for m in metrics) / len(metrics)
            avg_style_violations = sum(m["style_violations"] for m in metrics) / len(metrics)
        else:
            avg_complexity = avg_security_issues = avg_style_violations = 0
        
        conn.close()
        
        return {
            "success": True,
            "metrics": metrics,
            "summary": {
                "total_files": len(metrics),
                "average_complexity": avg_complexity,
                "average_security_issues": avg_security_issues,
                "average_style_violations": avg_style_violations
            }
        }
    
    def configure(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Update analyzer configuration"""
        try:
            # Validate configuration
            valid_keys = set(self.config.keys())
            provided_keys = set(config.keys())
            invalid_keys = provided_keys - valid_keys
            
            if invalid_keys:
                return {
                    "success": False,
                    "error": f"Invalid configuration keys: {list(invalid_keys)}"
                }
            
            # Update configuration
            self.config.update(config)
            
            return {
                "success": True,
                "updated_config": config,
                "current_config": self.config
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_status(self) -> Dict[str, Any]:
        """Get code analyzer status"""
        return {
            "name": self.name,
            "version": self.version,
            "status": "active",
            "config": self.config,
            "supported_languages": self.config["supported_extensions"],
            "security_categories": list(self.security_patterns.keys()),
            "timestamp": datetime.now().isoformat()
        }

# Helper classes for AST analysis
class ComplexityVisitor(ast.NodeVisitor):
    def __init__(self):
        self.total_complexity = 0
        self.max_function_complexity = 0
        self.complex_functions = []
        self.current_function = None
        self.current_complexity = 0
    
    def visit_FunctionDef(self, node):
        self.current_function = node.name
        self.current_complexity = 1  # Base complexity
        
        self.generic_visit(node)
        
        if self.current_complexity > self.max_function_complexity:
            self.max_function_complexity = self.current_complexity
        
        if self.current_complexity > 10:  # Threshold for complex functions
            self.complex_functions.append({
                "name": node.name,
                "line": node.lineno,
                "complexity": self.current_complexity
            })
        
        self.total_complexity += self.current_complexity
        self.current_function = None
        self.current_complexity = 0
    
    def visit_If(self, node):
        self.current_complexity += 1
        self.generic_visit(node)
    
    def visit_While(self, node):
        self.current_complexity += 1
        self.generic_visit(node)
    
    def visit_For(self, node):
        self.current_complexity += 1
        self.generic_visit(node)
    
    def visit_And(self, node):
        self.current_complexity += 1
        self.generic_visit(node)
    
    def visit_Or(self, node):
        self.current_complexity += 1
        self.generic_visit(node)
    
    @property
    def average_complexity(self):
        function_count = len(self.complex_functions)
        return self.total_complexity / function_count if function_count > 0 else 0

class StructureVisitor(ast.NodeVisitor):
    def __init__(self):
        self.functions = []
        self.classes = []
        self.imports = []
    
    def visit_FunctionDef(self, node):
        self.functions.append({
            "name": node.name,
            "line": node.lineno,
            "args_count": len(node.args.args)
        })
        self.generic_visit(node)
    
    def visit_ClassDef(self, node):
        methods = []
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                methods.append(item.name)
        
        self.classes.append({
            "name": node.name,
            "line": node.lineno,
            "methods": methods,
            "method_count": len(methods)
        })
        self.generic_visit(node)
    
    def visit_Import(self, node):
        for alias in node.names:
            self.imports.append({
                "name": alias.name,
                "alias": alias.asname,
                "line": node.lineno
            })
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node):
        if node.module:
            for alias in node.names:
                self.imports.append({
                    "name": f"{node.module}.{alias.name}",
                    "alias": alias.asname,
                    "line": node.lineno
                })
        self.generic_visit(node)

# Global instance
code_analyzer = CodeAnalyzer()