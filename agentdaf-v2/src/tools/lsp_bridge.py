#!/usr/bin/env python3
"""
LSP (Language Server Protocol) Bridge for AgentDaf1.1
Connects MCP servers with LSP capabilities for enhanced code analysis
"""

import json
import asyncio
import subprocess
import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import pathlib
import os

try:
    import docker
    from docker.models.containers import Container
except ImportError:
    docker = None
    Container = None

class LSPBridge:
    """Bridge between MCP servers and LSP capabilities"""
    
    def __init__(self, workspace_path: str = None):
        self.workspace_path = workspace_path or os.getcwd()
        self.client: Optional[Any] = None
        self.lsp_servers: Dict[str, Dict] = {}
        self.mcp_connections: Dict[str, Any] = {}
        self.logger = self._setup_logger()
        
    def _setup_logger(self) -> logging.Logger:
        """Setup logging for LSP bridge"""
        logger = logging.getLogger("LSPBridge")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
        return logger
    
    async def initialize(self) -> bool:
        """Initialize LSP bridge and connections"""
        try:
            self.logger.info("Initializing LSP Bridge...")
            
            # Initialize Docker client if available
            if docker:
                self.client = docker.from_env()
                self.logger.info("Docker client initialized")
            
            # Setup default LSP servers
            await self._setup_default_servers()
            
            # Connect to MCP servers
            await self._connect_mcp_servers()
            
            self.logger.info("LSP Bridge initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize LSP Bridge: {e}")
            return False
    
    async def _setup_default_servers(self):
        """Setup default LSP servers"""
        default_servers = {
            "python": {
                "command": ["pylsp"],
                "language": "python",
                "file_extensions": [".py"],
                "capabilities": [
                    "completion",
                    "hover",
                    "definition",
                    "references",
                    "diagnostics",
                    "formatting"
                ]
            },
            "javascript": {
                "command": ["typescript-language-server", "--stdio"],
                "language": "javascript",
                "file_extensions": [".js", ".jsx", ".ts", ".tsx"],
                "capabilities": [
                    "completion",
                    "hover",
                    "definition",
                    "references",
                    "diagnostics",
                    "formatting"
                ]
            },
            "json": {
                "command": ["vscode-json-language-server", "--stdio"],
                "language": "json",
                "file_extensions": [".json"],
                "capabilities": [
                    "completion",
                    "hover",
                    "validation",
                    "formatting"
                ]
            }
        }
        
        for name, config in default_servers.items():
            await self.register_lsp_server(name, config)
    
    async def register_lsp_server(self, name: str, config: Dict):
        """Register an LSP server"""
        try:
            self.lsp_servers[name] = {
                "name": name,
                "config": config,
                "process": None,
                "initialized": False,
                "capabilities": config.get("capabilities", [])
            }
            
            self.logger.info(f"Registered LSP server: {name}")
            
        except Exception as e:
            self.logger.error(f"Failed to register LSP server {name}: {e}")
    
    async def _connect_mcp_servers(self):
        """Connect to available MCP servers"""
        mcp_servers = {
            "sequential_thinking": {
                "url": "http://localhost:3010",
                "capabilities": ["analysis", "code_review", "optimization"]
            },
            "code_interpreter": {
                "url": "http://localhost:3011", 
                "capabilities": ["execution", "debugging", "testing"]
            }
        }
        
        for name, config in mcp_servers.items():
            try:
                # Test connection
                import requests
                response = requests.get(f"{config['url']}/health", timeout=5)
                if response.status_code == 200:
                    self.mcp_connections[name] = config
                    self.logger.info(f"Connected to MCP server: {name}")
                else:
                    self.logger.warning(f"MCP server {name} not healthy")
            except Exception as e:
                self.logger.warning(f"Failed to connect to MCP server {name}: {e}")
    
    async def analyze_code(self, file_path: str, analysis_type: str = "comprehensive") -> Dict:
        """Analyze code using both LSP and MCP capabilities"""
        try:
            file_path_obj = pathlib.Path(file_path)
            if not file_path_obj.exists():
                return {"error": f"File not found: {file_path}"}
            
            # Determine language and LSP server
            language = self._detect_language(file_path_obj)
            lsp_server = self._get_lsp_server_for_language(language)
            
            results = {
                "file_path": str(file_path_obj),
                "language": language,
                "timestamp": datetime.now().isoformat(),
                "analysis_type": analysis_type,
                "lsp_analysis": None,
                "mcp_analysis": None
            }
            
            # LSP Analysis
            if lsp_server:
                results["lsp_analysis"] = await self._perform_lsp_analysis(
                    file_path_obj, lsp_server, analysis_type
                )
            
            # MCP Analysis
            results["mcp_analysis"] = await self._perform_mcp_analysis(
                file_path_obj, analysis_type
            )
            
            return results
            
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
            ".css": "css",
            ".md": "markdown"
        }
        
        return language_map.get(extension, "unknown")
    
    def _get_lsp_server_for_language(self, language: str) -> Optional[str]:
        """Get LSP server name for language"""
        for name, server in self.lsp_servers.items():
            if server["config"].get("language") == language:
                return name
        return None
    
    async def _perform_lsp_analysis(self, file_path: pathlib.Path, server_name: str, analysis_type: str) -> Dict:
        """Perform LSP-based analysis"""
        try:
            server = self.lsp_servers[server_name]
            
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            analysis = {
                "server": server_name,
                "capabilities_used": [],
                "results": {}
            }
            
            # Simulate LSP analysis (in real implementation, would communicate with LSP server)
            capabilities = server["capabilities"]
            
            if "diagnostics" in capabilities and analysis_type in ["comprehensive", "diagnostics"]:
                analysis["capabilities_used"].append("diagnostics")
                analysis["results"]["diagnostics"] = self._simulate_diagnostics(content)
            
            if "completion" in capabilities and analysis_type in ["comprehensive", "completion"]:
                analysis["capabilities_used"].append("completion")
                analysis["results"]["completion"] = self._simulate_completion(content)
            
            if "hover" in capabilities and analysis_type in ["comprehensive", "hover"]:
                analysis["capabilities_used"].append("hover")
                analysis["results"]["hover"] = self._simulate_hover(content)
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"LSP analysis failed: {e}")
            return {"error": str(e)}
    
    async def _perform_mcp_analysis(self, file_path: pathlib.Path, analysis_type: str) -> Dict:
        """Perform MCP-based analysis"""
        try:
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            mcp_results = {}
            
            # Use sequential thinking MCP server for code analysis
            if "sequential_thinking" in self.mcp_connections:
                mcp_results["sequential_thinking"] = await self._analyze_with_sequential_thinking(
                    content, str(file_path), analysis_type
                )
            
            # Use code interpreter MCP server for execution/testing
            if "code_interpreter" in self.mcp_connections and analysis_type in ["comprehensive", "testing"]:
                mcp_results["code_interpreter"] = await self._analyze_with_code_interpreter(
                    content, str(file_path)
                )
            
            return mcp_results
            
        except Exception as e:
            self.logger.error(f"MCP analysis failed: {e}")
            return {"error": str(e)}
    
    def _simulate_diagnostics(self, content: str) -> List[Dict]:
        """Simulate LSP diagnostics"""
        diagnostics = []
        lines = content.split('/n')
        
        for i, line in enumerate(lines, 1):
            # Simple checks for common issues
            if line.strip() and not line.endswith(':') and not line.endswith(';') and not line.endswith(','):
                if any(keyword in line for keyword in ['def ', 'class ', 'if ', 'for ', 'while ']):
                    if ':' not in line:
                        diagnostics.append({
                            "line": i,
                            "column": len(line),
                            "severity": "warning",
                            "message": "Missing colon at end of statement",
                            "source": "pylsp"
                        })
        
        return diagnostics
    
    def _simulate_completion(self, content: str) -> List[Dict]:
        """Simulate LSP completion"""
        return [
            {"label": "def ", "kind": "snippet", "detail": "Function definition"},
            {"label": "class ", "kind": "snippet", "detail": "Class definition"},
            {"label": "import ", "kind": "snippet", "detail": "Import statement"},
            {"label": "if __name__", "kind": "snippet", "detail": "Main guard"}
        ]
    
    def _simulate_hover(self, content: str) -> Dict:
        """Simulate LSP hover information"""
        return {
            "contents": {
                "kind": "markdown",
                "value": "Hover information not available in simulation"
            }
        }
    
    async def _analyze_with_sequential_thinking(self, content: str, file_path: str, analysis_type: str) -> Dict:
        """Analyze code using sequential thinking MCP server"""
        try:
            import requests
            
            prompt = f"""
            Analyze this code file: {file_path}
            
            Analysis type: {analysis_type}
            
            Content:
            {content[:2000]}...
            
            Please provide:
            1. Code quality assessment
            2. Potential improvements
            3. Security considerations
            4. Performance implications
            5. Best practices compliance
            """
            
            payload = {
                "prompt": prompt,
                "context": {"file_path": file_path, "analysis_type": analysis_type},
                "timestamp": datetime.now().isoformat()
            }
            
            response = requests.post(
                "http://localhost:3010/api/think",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"MCP server error: {response.status_code}"}
                
        except Exception as e:
            return {"error": f"Sequential thinking analysis failed: {e}"}
    
    async def _analyze_with_code_interpreter(self, content: str, file_path: str) -> Dict:
        """Analyze code using code interpreter MCP server"""
        try:
            import requests
            
            payload = {
                "code": content,
                "file_path": file_path,
                "action": "analyze",
                "timestamp": datetime.now().isoformat()
            }
            
            response = requests.post(
                "http://localhost:3011/api/analyze",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"Code interpreter error: {response.status_code}"}
                
        except Exception as e:
            return {"error": f"Code interpreter analysis failed: {e}"}
    
    async def get_completions(self, file_path: str, line: int, column: int) -> List[Dict]:
        """Get code completions"""
        try:
            file_path_obj = pathlib.Path(file_path)
            language = self._detect_language(file_path_obj)
            server_name = self._get_lsp_server_for_language(language)
            
            if not server_name:
                return []
            
            # Simulate completions (in real implementation, would query LSP server)
            return self._simulate_completion("")
            
        except Exception as e:
            self.logger.error(f"Failed to get completions: {e}")
            return []
    
    async def get_diagnostics(self, file_path: str) -> List[Dict]:
        """Get diagnostic information for file"""
        try:
            result = await self.analyze_code(file_path, "diagnostics")
            
            if result.get("lsp_analysis", {}).get("results", {}).get("diagnostics"):
                return result["lsp_analysis"]["results"]["diagnostics"]
            
            return []
            
        except Exception as e:
            self.logger.error(f"Failed to get diagnostics: {e}")
            return []
    
    async def format_code(self, file_path: str) -> Dict:
        """Format code using LSP"""
        try:
            file_path_obj = pathlib.Path(file_path)
            language = self._detect_language(file_path_obj)
            server_name = self._get_lsp_server_for_language(language)
            
            if not server_name:
                return {"error": f"No LSP server for language: {language}"}
            
            # Read original content
            with open(file_path_obj, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            # Simulate formatting (in real implementation, would use LSP server)
            formatted_content = self._simulate_formatting(original_content, language)
            
            # Write formatted content
            with open(file_path_obj, 'w', encoding='utf-8') as f:
                f.write(formatted_content)
            
            return {
                "success": True,
                "file_path": str(file_path_obj),
                "language": language,
                "server": server_name
            }
            
        except Exception as e:
            self.logger.error(f"Failed to format code: {e}")
            return {"error": str(e)}
    
    def _simulate_formatting(self, content: str, language: str) -> str:
        """Simulate code formatting"""
        # Basic formatting simulation
        lines = content.split('/n')
        formatted_lines = []
        
        for line in lines:
            # Basic indentation fix
            if line.strip():
                if not line.startswith(' ') and not line.startswith('/t'):
                    # Add basic indentation for certain constructs
                    if any(line.strip().startswith(keyword) for keyword in ['def ', 'class ', 'if ', 'for ', 'while ', 'try:']):
                        formatted_lines.append(line)
                    else:
                        formatted_lines.append('    ' + line if line.strip() else line)
                else:
                    formatted_lines.append(line)
            else:
                formatted_lines.append(line)
        
        return '/n'.join(formatted_lines)
    
    async def shutdown(self):
        """Shutdown LSP bridge and cleanup connections"""
        try:
            self.logger.info("Shutting down LSP Bridge...")
            
            # Close LSP server processes
            for server_name, server in self.lsp_servers.items():
                if server.get("process"):
                    try:
                        server["process"].terminate()
                        self.logger.info(f"Terminated LSP server: {server_name}")
                    except Exception as e:
                        self.logger.error(f"Failed to terminate LSP server {server_name}: {e}")
            
            # Clear connections
            self.lsp_servers.clear()
            self.mcp_connections.clear()
            
            self.logger.info("LSP Bridge shutdown complete")
            
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")

# CLI Interface
async def main():
    """CLI interface for LSP Bridge"""
    import argparse
    
    parser = argparse.ArgumentParser(description="LSP Bridge for AgentDaf1.1")
    parser.add_argument("--workspace", "-w", help="Workspace path", default=".")
    parser.add_argument("--analyze", "-a", help="Analyze file")
    parser.add_argument("--format", "-f", help="Format file")
    parser.add_argument("--diagnostics", "-d", help="Get diagnostics for file")
    parser.add_argument("--test", "-t", action="store_true", help="Test LSP bridge")
    
    args = parser.parse_args()
    
    bridge = LSPBridge(args.workspace)
    
    if not await bridge.initialize():
        logger.info("❌ Failed to initialize LSP Bridge")
        return
    
    try:
        if args.analyze:
            result = await bridge.analyze_code(args.analyze)
            logger.info(json.dumps(result, indent=2))
        elif args.format:
            result = await bridge.format_code(args.format)
            logger.info(json.dumps(result, indent=2))
        elif args.diagnostics:
            diagnostics = await bridge.get_diagnostics(args.diagnostics)
            logger.info(json.dumps(diagnostics, indent=2))
        elif args.test:
            logger.info("🧪 Testing LSP Bridge...")
            
            # Test with a sample Python file
            test_file = "test_lsp_sample.py"
            with open(test_file, 'w') as f:
                f.write("def hello_world():/nlogger.info('Hello, World!')/n")
            
            result = await bridge.analyze_code(test_file)
            logger.info("Analysis result:")
            logger.info(json.dumps(result, indent=2))
            
            # Cleanup
            os.remove(test_file)
            print("✅ LSP Bridge test completed")
        else:
            logger.info("LSP Bridge initialized. Use --help for options.")
            
    finally:
        await bridge.shutdown()

if __name__ == "__main__":
    asyncio.run(main())