#!/usr/bin/env python3
"""
Language Server Capabilities for AgentDaf1.1
Enhanced code analysis with LSP features
"""

import json
import asyncio
import subprocess
import tempfile
import os
import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import pathlib
import ast
import logging

class LanguageServerCapabilities:
    """Enhanced language server capabilities for code analysis"""
    
    def __init__(self):
        self.logger = self._setup_logger()
        self.supported_languages = {
            "python": self._get_python_capabilities(),
            "javascript": self._get_javascript_capabilities(),
            "json": self._get_json_capabilities(),
            "html": self._get_html_capabilities(),
            "css": self._get_css_capabilities()
        }
        
    def _setup_logger(self) -> logging.Logger:
        """Setup logging"""
        logger = logging.getLogger("LanguageServerCapabilities")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
        return logger
    
    def _get_python_capabilities(self) -> Dict:
        """Get Python language server capabilities"""
        return {
            "completion": {
                "enabled": True,
                "trigger_characters": [".", "(", "[", " "],
                "providers": ["snippets", "keywords", "imports", "functions", "classes"]
            },
            "hover": {
                "enabled": True,
                "content_format": ["markdown", "plaintext"]
            },
            "definition": {
                "enabled": True,
                "support_location_link": True
            },
            "references": {
                "enabled": True,
                "include_declaration": True
            },
            "diagnostics": {
                "enabled": True,
                "severity_levels": ["error", "warning", "info", "hint"],
                "providers": ["syntax", "semantic", "style"]
            },
            "formatting": {
                "enabled": True,
                "providers": ["black", "autopep8", "yapf"]
            },
            "code_actions": {
                "enabled": True,
                "kinds": ["quickfix", "refactor", "source.organizeImports"]
            },
            "symbols": {
                "enabled": True,
                "kinds": ["file", "module", "namespace", "package", "class", "method", "property", "field", "constructor", "enum", "interface", "function", "variable", "constant", "string", "number", "boolean", "array"]
            }
        }
    
    def _get_javascript_capabilities(self) -> Dict:
        """Get JavaScript language server capabilities"""
        return {
            "completion": {
                "enabled": True,
                "trigger_characters": [".", "(", "[", " ", "\"", "'"],
                "providers": ["snippets", "keywords", "imports", "functions", "classes"]
            },
            "hover": {
                "enabled": True,
                "content_format": ["markdown", "plaintext"]
            },
            "definition": {
                "enabled": True,
                "support_location_link": True
            },
            "diagnostics": {
                "enabled": True,
                "severity_levels": ["error", "warning", "info", "hint"],
                "providers": ["eslint", "typescript"]
            },
            "formatting": {
                "enabled": True,
                "providers": ["prettier", "eslint"]
            }
        }
    
    def _get_json_capabilities(self) -> Dict:
        """Get JSON language server capabilities"""
        return {
            "completion": {
                "enabled": True,
                "trigger_characters": ["\"", ":", ",", "[", "{"],
                "providers": ["schema", "properties"]
            },
            "validation": {
                "enabled": True,
                "severity_levels": ["error", "warning"]
            },
            "formatting": {
                "enabled": True,
                "providers": ["prettier"]
            }
        }
    
    def _get_html_capabilities(self) -> Dict:
        """Get HTML language server capabilities"""
        return {
            "completion": {
                "enabled": True,
                "trigger_characters": ["<", " ", "\"", "'"],
                "providers": ["tags", "attributes", "values"]
            },
            "validation": {
                "enabled": True,
                "severity_levels": ["error", "warning"]
            },
            "formatting": {
                "enabled": True,
                "providers": ["prettier", "html-beautify"]
            }
        }
    
    def _get_css_capabilities(self) -> Dict:
        """Get CSS language server capabilities"""
        return {
            "completion": {
                "enabled": True,
                "trigger_characters": [" ", ":", "{", "!", "-"],
                "providers": ["properties", "values", "selectors"]
            },
            "validation": {
                "enabled": True,
                "severity_levels": ["error", "warning"]
            },
            "formatting": {
                "enabled": True,
                "providers": ["prettier", "css-beautify"]
            }
        }
    
    async def analyze_code(self, file_path: str, analysis_options: Dict = None) -> Dict:
        """Perform comprehensive code analysis"""
        try:
            file_path_obj = pathlib.Path(file_path)
            if not file_path_obj.exists():
                return {"error": f"File not found: {file_path}"}
            
            # Detect language
            language = self._detect_language(file_path_obj)
            if language not in self.supported_languages:
                return {"error": f"Unsupported language: {language}"}
            
            # Read file content
            with open(file_path_obj, 'r', encoding='utf-8') as f:
                content = f.read()
            
            analysis_options = analysis_options or {}
            
            result = {
                "file_path": str(file_path_obj),
                "language": language,
                "timestamp": datetime.now().isoformat(),
                "capabilities": self.supported_languages[language],
                "analysis": {}
            }
            
            # Perform different types of analysis
            if analysis_options.get("diagnostics", True):
                result["analysis"]["diagnostics"] = await self._analyze_diagnostics(
                    content, language
                )
            
            if analysis_options.get("symbols", True):
                result["analysis"]["symbols"] = await self._analyze_symbols(
                    content, language
                )
            
            if analysis_options.get("complexity", True):
                result["analysis"]["complexity"] = await self._analyze_complexity(
                    content, language
                )
            
            if analysis_options.get("metrics", True):
                result["analysis"]["metrics"] = await self._analyze_metrics(
                    content, language
                )
            
            if analysis_options.get("security", False):
                result["analysis"]["security"] = await self._analyze_security(
                    content, language
                )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Code analysis failed: {e}")
            return {"error": str(e)}
    
    def _detect_language(self, file_path: pathlib.Path) -> str:
        """Detect programming language from file extension"""
        extension = file_path.suffix.lower()
        
        language_map = {
            ".py": "python",
            ".js": "javascript",
            ".jsx": "javascript",
            ".ts": "javascript",
            ".tsx": "javascript",
            ".json": "json",
            ".html": "html",
            ".htm": "html",
            ".css": "css",
            ".scss": "css",
            ".sass": "css",
            ".less": "css"
        }
        
        return language_map.get(extension, "unknown")
    
    async def _analyze_diagnostics(self, content: str, language: str) -> Dict:
        """Analyze code for diagnostics"""
        diagnostics = {
            "errors": [],
            "warnings": [],
            "info": [],
            "hints": []
        }
        
        if language == "python":
            diagnostics = await self._python_diagnostics(content)
        elif language == "javascript":
            diagnostics = await self._javascript_diagnostics(content)
        elif language == "json":
            diagnostics = await self._json_diagnostics(content)
        elif language == "html":
            diagnostics = await self._html_diagnostics(content)
        elif language == "css":
            diagnostics = await self._css_diagnostics(content)
        
        return diagnostics
    
    async def _python_diagnostics(self, content: str) -> Dict:
        """Python-specific diagnostics"""
        diagnostics = {"errors": [], "warnings": [], "info": [], "hints": []}
        
        try:
            # Parse AST to detect syntax errors
            ast.parse(content)
        except SyntaxError as e:
            diagnostics["errors"].append({
                "line": e.lineno or 1,
                "column": e.offset or 0,
                "message": f"Syntax error: {e.msg}",
                "severity": "error",
                "source": "python-ast"
            })
        
        lines = content.split('/n')
        
        for i, line in enumerate(lines, 1):
            # Check for common issues
            if line.strip() and not line.endswith(':') and not line.endswith(';') and not line.endswith(','):
                if any(keyword in line for keyword in ['def ', 'class ', 'if ', 'for ', 'while ', 'try:', 'except', 'with ']):
                    if ':' not in line and not line.strip().endswith(':'):
                        diagnostics["warnings"].append({
                            "line": i,
                            "column": len(line),
                            "message": "Missing colon at end of statement",
                            "severity": "warning",
                            "source": "python-style"
                        })
            
            # Check for unused imports (basic check)
            if line.strip().startswith('import ') or line.strip().startswith('from '):
                import_name = line.strip().split()[-1].replace(';', '').replace(',', '')
                if import_name not in content.replace(line, ''):
                    diagnostics["info"].append({
                        "line": i,
                        "column": 0,
                        "message": f"Potentially unused import: {import_name}",
                        "severity": "info",
                        "source": "python-unused"
                    })
        
        return diagnostics
    
    async def _javascript_diagnostics(self, content: str) -> Dict:
        """JavaScript-specific diagnostics"""
        diagnostics = {"errors": [], "warnings": [], "info": [], "hints": []}
        
        lines = content.split('/n')
        
        for i, line in enumerate(lines, 1):
            # Check for missing semicolons
            if line.strip() and not line.strip().endswith(';') and not line.strip().endswith('{') and not line.strip().endswith('}'):
                if any(keyword in line for keyword in ['var ', 'let ', 'const ', 'return ', 'console.']):
                    diagnostics["warnings"].append({
                        "line": i,
                        "column": len(line),
                        "message": "Missing semicolon",
                        "severity": "warning",
                        "source": "javascript-style"
                    })
            
            # Check for console.log statements
            if 'console.log' in line:
                diagnostics["info"].append({
                    "line": i,
                    "column": line.find('console.log'),
                    "message": "Console.log statement found",
                    "severity": "info",
                    "source": "javascript-debug"
                })
        
        return diagnostics
    
    async def _json_diagnostics(self, content: str) -> Dict:
        """JSON-specific diagnostics"""
        diagnostics = {"errors": [], "warnings": [], "info": [], "hints": []}
        
        try:
            json.loads(content)
        except json.JSONDecodeError as e:
            diagnostics["errors"].append({
                "line": e.lineno or 1,
                "column": e.colno or 0,
                "message": f"JSON syntax error: {e.msg}",
                "severity": "error",
                "source": "json-parser"
            })
        
        return diagnostics
    
    async def _html_diagnostics(self, content: str) -> Dict:
        """HTML-specific diagnostics"""
        diagnostics = {"errors": [], "warnings": [], "info": [], "hints": []}
        
        # Basic HTML validation
        lines = content.split('/n')
        
        for i, line in enumerate(lines, 1):
            # Check for unclosed tags (basic)
            if '<' in line and '>' not in line:
                diagnostics["warnings"].append({
                    "line": i,
                    "column": line.find('<'),
                    "message": "Unclosed HTML tag",
                    "severity": "warning",
                    "source": "html-validator"
                })
        
        return diagnostics
    
    async def _css_diagnostics(self, content: str) -> Dict:
        """CSS-specific diagnostics"""
        diagnostics = {"errors": [], "warnings": [], "info": [], "hints": []}
        
        lines = content.split('/n')
        
        for i, line in enumerate(lines, 1):
            # Check for missing semicolons
            if line.strip() and not line.strip().endswith(';') and not line.strip().endswith('{') and not line.strip().endswith('}'):
                if ':' in line and not line.strip().endswith(':'):
                    diagnostics["warnings"].append({
                        "line": i,
                        "column": len(line),
                        "message": "Missing semicolon",
                        "severity": "warning",
                        "source": "css-style"
                    })
        
        return diagnostics
    
    async def _analyze_symbols(self, content: str, language: str) -> Dict:
        """Analyze code symbols"""
        symbols = {
            "classes": [],
            "functions": [],
            "variables": [],
            "imports": []
        }
        
        if language == "python":
            symbols = await self._python_symbols(content)
        elif language == "javascript":
            symbols = await self._javascript_symbols(content)
        
        return symbols
    
    async def _python_symbols(self, content: str) -> Dict:
        """Extract Python symbols"""
        symbols = {"classes": [], "functions": [], "variables": [], "imports": []}
        
        try:
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    symbols["classes"].append({
                        "name": node.name,
                        "line": node.lineno,
                        "column": node.col_offset,
                        "type": "class"
                    })
                elif isinstance(node, ast.FunctionDef):
                    symbols["functions"].append({
                        "name": node.name,
                        "line": node.lineno,
                        "column": node.col_offset,
                        "type": "function"
                    })
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        symbols["imports"].append({
                            "name": alias.name,
                            "line": node.lineno,
                            "column": node.col_offset,
                            "type": "import"
                        })
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    for alias in node.names:
                        symbols["imports"].append({
                            "name": f"{module}.{alias.name}",
                            "line": node.lineno,
                            "column": node.col_offset,
                            "type": "import"
                        })
                        
        except Exception as e:
            self.logger.error(f"Python symbol analysis failed: {e}")
        
        return symbols
    
    async def _javascript_symbols(self, content: str) -> Dict:
        """Extract JavaScript symbols"""
        symbols = {"classes": [], "functions": [], "variables": [], "imports": []}
        
        lines = content.split('/n')
        
        for i, line in enumerate(lines, 1):
            # Class detection
            class_match = re.search(r'class/s+(/w+)', line)
            if class_match:
                symbols["classes"].append({
                    "name": class_match.group(1),
                    "line": i,
                    "column": class_match.start(),
                    "type": "class"
                })
            
            # Function detection
            func_match = re.search(r'function/s+(/w+)', line)
            if func_match:
                symbols["functions"].append({
                    "name": func_match.group(1),
                    "line": i,
                    "column": func_match.start(),
                    "type": "function"
                })
            
            # Variable detection
            var_match = re.search(r'(?:var|let|const)/s+(/w+)', line)
            if var_match:
                symbols["variables"].append({
                    "name": var_match.group(1),
                    "line": i,
                    "column": var_match.start(),
                    "type": "variable"
                })
            
            # Import detection
            import_match = re.search(r'import.*from\s+[\'"]([^\'"]+)[\'"]', line)
            if import_match:
                symbols["imports"].append({
                    "name": import_match.group(1),
                    "line": i,
                    "column": import_match.start(),
                    "type": "import"
                })
        
        return symbols
    
    async def _analyze_complexity(self, content: str, language: str) -> Dict:
        """Analyze code complexity"""
        complexity = {
            "cyclomatic_complexity": 0,
            "cognitive_complexity": 0,
            "lines_of_code": len(content.split('/n')),
            "logical_lines": 0,
            "comment_lines": 0,
            "blank_lines": 0
        }
        
        lines = content.split('/n')
        
        for line in lines:
            stripped = line.strip()
            if not stripped:
                complexity["blank_lines"] += 1
            elif stripped.startswith('#') or stripped.startswith('//') or stripped.startswith('/*') or stripped.startswith('*'):
                complexity["comment_lines"] += 1
            else:
                complexity["logical_lines"] += 1
        
        # Calculate cyclomatic complexity (basic)
        if language == "python":
            complexity["cyclomatic_complexity"] = content.count('if ') + content.count('elif ') + content.count('for ') + content.count('while ') + content.count('except') + 1
        elif language == "javascript":
            complexity["cyclomatic_complexity"] = content.count('if(') + content.count('for(') + content.count('while(') + content.count('catch(') + content.count('case ') + 1
        
        return complexity
    
    async def _analyze_metrics(self, content: str, language: str) -> Dict:
        """Analyze code metrics"""
        metrics = {
            "maintainability_index": 0,
            "technical_debt_ratio": 0,
            "code_duplication": 0,
            "test_coverage": 0,
            "documentation_coverage": 0
        }
        
        # Calculate maintainability index (simplified)
        lines = content.split('/n')
        total_lines = len(lines)
        comment_lines = sum(1 for line in lines if line.strip().startswith(('#', '//', '/*', '*')))
        
        if total_lines > 0:
            metrics["documentation_coverage"] = (comment_lines / total_lines) * 100
        
        # Simplified maintainability index
        complexity = await self._analyze_complexity(content, language)
        if complexity["logical_lines"] > 0:
            metrics["maintainability_index"] = max(0, 100 - (complexity["cyclomatic_complexity"] * 2))
        
        return metrics
    
    async def _analyze_security(self, content: str, language: str) -> Dict:
        """Analyze security issues"""
        security = {
            "vulnerabilities": [],
            "security_score": 100,
            "recommendations": []
        }
        
        # Common security patterns to check
        security_patterns = {
            "python": [
                (r'eval/s*/(', "Use of eval() function is dangerous"),
                (r'exec/s*/(', "Use of exec() function is dangerous"),
                (r'shell=True', "shell=True in subprocess can be dangerous"),
                (r'pickle/.loads?/s*/(', "Pickle can execute arbitrary code"),
                (r'input/s*/(', "input() without validation can be risky")
            ],
            "javascript": [
                (r'eval/s*/(', "Use of eval() function is dangerous"),
                (r'innerHTML/s*=', "innerHTML can lead to XSS"),
                (r'document/.write/s*/(', "document.write can lead to XSS"),
                (r'setTimeout\s*\(\s*["\']', "setTimeout with string can be dangerous")
            ]
        }
        
        patterns = security_patterns.get(language, [])
        
        for pattern, message in patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                line_num = content[:match.start()].count('/n') + 1
                security["vulnerabilities"].append({
                    "line": line_num,
                    "column": match.start() - content.rfind('/n', 0, match.start()) - 1,
                    "message": message,
                    "severity": "warning",
                    "pattern": pattern
                })
                
                security["security_score"] -= 10
        
        security["recommendations"] = [
            "Validate all user inputs",
            "Use parameterized queries for database operations",
            "Implement proper error handling",
            "Keep dependencies updated",
            "Use HTTPS for all communications"
        ]
        
        return security
    
    async def get_completions(self, file_path: str, line: int, column: int, context: str = "") -> List[Dict]:
        """Get code completions"""
        try:
            file_path_obj = pathlib.Path(file_path)
            language = self._detect_language(file_path_obj)
            
            completions = []
            
            if language == "python":
                completions = await self._python_completions(context)
            elif language == "javascript":
                completions = await self._javascript_completions(context)
            elif language == "json":
                completions = await self._json_completions(context)
            
            return completions
            
        except Exception as e:
            self.logger.error(f"Failed to get completions: {e}")
            return []
    
    async def _python_completions(self, context: str) -> List[Dict]:
        """Python completions"""
        completions = []
        
        # Python keywords
        python_keywords = [
            "def ", "class ", "if ", "elif ", "else:", "for ", "while ", "try:", "except", "finally:",
            "with ", "import ", "from ", "as ", "return ", "yield ", "lambda ", "pass", "break", "continue",
            "and", "or", "not", "in", "is", "None", "True", "False"
        ]
        
        for keyword in python_keywords:
            completions.append({
                "label": keyword,
                "kind": "keyword",
                "detail": f"Python keyword: {keyword}",
                "insert_text": keyword,
                "priority": 1
            })
        
        # Common modules
        modules = ["os", "sys", "json", "datetime", "requests", "pandas", "numpy", "asyncio", "logging"]
        for module in modules:
            completions.append({
                "label": f"import {module}",
                "kind": "module",
                "detail": f"Import {module} module",
                "insert_text": f"import {module}",
                "priority": 2
            })
        
        return completions
    
    async def _javascript_completions(self, context: str) -> List[Dict]:
        """JavaScript completions"""
        completions = []
        
        # JavaScript keywords
        js_keywords = [
            "function ", "const ", "let ", "var ", "if ", "else", "for ", "while ", "do ", "switch ",
            "case ", "break", "continue", "return ", "class ", "extends", "import ", "export ", "try ", "catch", "finally"
        ]
        
        for keyword in js_keywords:
            completions.append({
                "label": keyword,
                "kind": "keyword",
                "detail": f"JavaScript keyword: {keyword}",
                "insert_text": keyword,
                "priority": 1
            })
        
        return completions
    
    async def _json_completions(self, context: str) -> List[Dict]:
        """JSON completions"""
        completions = []
        
        # JSON structure templates
        templates = [
            ('{"key": "value"}', "Object template"),
            ('[]', "Array template"),
            ('true', "Boolean true"),
            ('false', "Boolean false"),
            ('null', "Null value")
        ]
        
        for template, detail in templates:
            completions.append({
                "label": template,
                "kind": "snippet",
                "detail": detail,
                "insert_text": template,
                "priority": 1
            })
        
        return completions

# CLI Interface
async def main():
    """CLI interface for Language Server Capabilities"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Language Server Capabilities for AgentDaf1.1")
    parser.add_argument("--analyze", "-a", help="Analyze file")
    parser.add_argument("--completions", "-c", help="Get completions for file")
    parser.add_argument("--line", "-l", type=int, help="Line number for completions")
    parser.add_argument("--column", type=int, default=0, help="Column number for completions")
    parser.add_argument("--security", "-s", action="store_true", help="Include security analysis")
    
    args = parser.parse_args()
    
    lsc = LanguageServerCapabilities()
    
    if args.analyze:
        options = {"security": args.security}
        result = await lsc.analyze_code(args.analyze, options)
        logger.info(json.dumps(result, indent=2))
    elif args.completions:
        if args.line is None:
            logger.info("Error: --line is required for completions")
            return
        
        completions = await lsc.get_completions(args.completions, args.line, args.column)
        logger.info(json.dumps(completions, indent=2))
    else:
        logger.info("Language Server Capabilities initialized. Use --help for options.")

if __name__ == "__main__":
    asyncio.run(main())