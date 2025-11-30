#!/usr/bin/env python3
"""
Simple MCP-LSP Connection Script
A working version that connects MCP and LSP functionality
"""

import asyncio
import json
import logging
import sys
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

class SimpleMCPLSPConnector:
    """Simplified MCP-LSP Connector"""
    
    def __init__(self, workspace_path: str = "."):
        self.workspace_path = workspace_path
        self.logger = self._setup_logger()
        self.mcp_servers = {}
        self.lsp_available = False
        
    def _setup_logger(self) -> logging.Logger:
        """Setup logging"""
        logger = logging.getLogger("SimpleMCPLSPConnector")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
        return logger
    
    async def test_mcp_connection(self) -> bool:
        """Test MCP server connection"""
        try:
            import requests
            
            # Test AgentDaf1 MCP server
            response = requests.get("http://localhost:8080/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.mcp_servers["agentdaf1"] = data
                self.logger.info("Connected to AgentDaf1 MCP Server")
                return True
            else:
                self.logger.warning(f"AgentDaf1 MCP Server returned {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.warning(f"Could not connect to MCP server: {e}")
            return False
    
    async def test_lsp_functionality(self) -> bool:
        """Test basic LSP functionality"""
        try:
            # Test if we can import LSP-related modules
            import subprocess
            
            # Check if pylsp is available
            result = subprocess.run(['pylsp', '--help'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                self.lsp_available = True
                self.logger.info("Python LSP (pylsp) is available")
                return True
            else:
                self.logger.warning("Python LSP (pylsp) not available")
                return False
                
        except Exception as e:
            self.logger.warning(f"LSP test failed: {e}")
            return False
    
    async def analyze_file_simple(self, file_path: str) -> Dict:
        """Simple file analysis using available tools"""
        try:
            if not os.path.exists(file_path):
                return {"error": f"File not found: {file_path}"}
            
            result = {
                "file_path": file_path,
                "timestamp": datetime.now().isoformat(),
                "mcp_analysis": None,
                "lsp_analysis": None,
                "basic_analysis": {}
            }
            
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Basic analysis
            lines = content.split('/n')
            result["basic_analysis"] = {
                "line_count": len(lines),
                "character_count": len(content),
                "language": self._detect_language(file_path),
                "has_functions": "def " in content,
                "has_classes": "class " in content,
                "has_imports": "import " in content
            }
            
            # MCP Analysis if available
            if self.mcp_servers:
                result["mcp_analysis"] = await self._mcp_analyze(content, file_path)
            
            # LSP Analysis if available
            if self.lsp_available:
                result["lsp_analysis"] = await self._lsp_analyze(content, file_path)
            
            return result
            
        except Exception as e:
            return {"error": str(e)}
    
    def _detect_language(self, file_path: str) -> str:
        """Detect programming language from file extension"""
        ext = Path(file_path).suffix.lower()
        language_map = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".json": "json",
            ".html": "html",
            ".css": "css",
            ".md": "markdown"
        }
        return language_map.get(ext, "unknown")
    
    async def _mcp_analyze(self, content: str, file_path: str) -> Dict:
        """Analyze using MCP server"""
        try:
            import requests
            
            # Simple MCP analysis request
            payload = {
                "action": "analyze",
                "content": content[:1000],  # Limit content
                "file_path": file_path,
                "timestamp": datetime.now().isoformat()
            }
            
            response = requests.post(
                "http://localhost:8080/mcp",
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"MCP server error: {response.status_code}"}
                
        except Exception as e:
            return {"error": f"MCP analysis failed: {e}"}
    
    async def _lsp_analyze(self, content: str, file_path: str) -> Dict:
        """Analyze using LSP (simplified)"""
        try:
# Simple static analysis
            lines = content.split('\n')
            issues = []
            
            for i, line in enumerate(lines, 1):
                line_stripped = line.strip()
                
                # Basic Python checks
                if line_stripped.startswith('def ') and ':' not in line:
                    issues.append({
                        "line": i,
                        "type": "syntax",
                        "message": "Function definition missing colon",
                        "severity": "error"
                    })
                elif line_stripped.startswith('class ') and ':' not in line:
                    issues.append({
                        "line": i,
                        "type": "syntax", 
                        "message": "Class definition missing colon",
                        "severity": "error"
                    })
                elif line_stripped and not line_stripped.endswith((':', ';', ',')) and \
                     any(keyword in line_stripped for keyword in ['if ', 'for ', 'while ', 'try:', 'except']):
                    if ':' not in line:
                        issues.append({
                            "line": i,
                            "type": "syntax",
                            "message": "Statement missing colon",
                            "severity": "warning"
                        })
            
            return {
                "server": "simple_lsp",
                "issues": issues,
                "issue_count": len(issues),
                "language": self._detect_language(file_path)
            }
            
        except Exception as e:
            return {"error": f"LSP analysis failed: {e}"}
    
    async def get_status(self) -> Dict:
        """Get connection status"""
        return {
            "timestamp": datetime.now().isoformat(),
            "workspace_path": self.workspace_path,
            "mcp_connected": len(self.mcp_servers) > 0,
            "mcp_servers": list(self.mcp_servers.keys()),
            "lsp_available": self.lsp_available,
            "status": "ready" if (self.mcp_servers or self.lsp_available) else "limited"
        }

async def main():
    """Main CLI interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Simple MCP-LSP Connector")
    parser.add_argument("--workspace", "-w", help="Workspace path", default=".")
    parser.add_argument("--test", "-t", action="store_true", help="Test connections")
    parser.add_argument("--analyze", "-a", help="Analyze file")
    parser.add_argument("--status", "-s", action="store_true", help="Show status")
    
    args = parser.parse_args()
    
    connector = SimpleMCPLSPConnector(args.workspace)
    
    try:
        if args.test:
            logger.info("Testing MCP-LSP Connections...")
            
            mcp_ok = await connector.test_mcp_connection()
            lsp_ok = await connector.test_lsp_functionality()
            
            logger.info(f"/nResults:")
            logger.info(f"   MCP Connection: {'OK' if mcp_ok else 'FAIL'}")
            logger.info(f"   LSP Available: {'OK' if lsp_ok else 'FAIL'}")
            
            if mcp_ok or lsp_ok:
                logger.info("Basic connectivity established!")
            else:
                logger.info("Limited functionality - no services available")
        
        elif args.analyze:
            logger.info(f"Analyzing file: {args.analyze}")
            
            # Test connections first
            await connector.test_mcp_connection()
            await connector.test_lsp_functionality()
            
            result = await connector.analyze_file_simple(args.analyze)
            logger.info(json.dumps(result, indent=2))
        
        elif args.status:
            # Test connections first
            await connector.test_mcp_connection()
            await connector.test_lsp_functionality()
            
            status = await connector.get_status()
            logger.info(json.dumps(status, indent=2))
        
        else:
            logger.info("Simple MCP-LSP Connector")
            logger.info("Use --help to see available options")
            logger.info("/nQuick examples:")
            print("  python simple_mcp_lsp_connect.py --test")
            logger.info("  python simple_mcp_lsp_connect.py --analyze app.py")
            logger.info("  python simple_mcp_lsp_connect.py --status")
    
    except KeyboardInterrupt:
        logger.info("/nGoodbye!")
    except Exception as e:
        logger.info(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())