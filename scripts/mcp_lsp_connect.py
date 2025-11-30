#!/usr/bin/env python3
"""
MCP-LSP Connection Script for AgentDaf1.1
Establishes and manages the connection between MCP servers and LSP capabilities
"""

import json
import asyncio
import logging
import subprocess
import sys
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# Add src to path for imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(project_root, 'src'))

try:
    from tools.mcp_lsp_interface import MCPLSPInterface
    from tools.lsp_bridge import LSPBridge
    from mcp.mcp_client import MCPClient
except ImportError as e:
    print(f"[ERROR] Import error: {e}")
    print(f"Project root: {project_root}")
    print("Please ensure you're running this from the project root")
    sys.exit(1)

class MCPLSPConnector:
    """Main connector class for MCP-LSP integration"""
    
    def __init__(self, workspace_path: str = None):
        self.workspace_path = workspace_path or os.getcwd()
        self.interface = None
        self.logger = self._setup_logger()
        self.mcp_servers = {}
        self.lsp_servers = {}
        self.connection_status = {
            "mcp_connected": False,
            "lsp_connected": False,
            "interface_running": False,
            "websocket_port": 8082
        }
        
    def _setup_logger(self) -> logging.Logger:
        """Setup logging"""
        logger = logging.getLogger("MCPLSPConnector")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
        return logger
    
    async def establish_connection(self) -> bool:
        """Establish connection between MCP and LSP"""
        try:
            self.logger.info("🔗 Establishing MCP-LSP Connection...")
            
            # Step 1: Initialize the interface
            self.interface = MCPLSPInterface(self.workspace_path)
            
            if not await self.interface.initialize():
                self.logger.error("❌ Failed to initialize MCP-LSP Interface")
                return False
            
            self.connection_status["interface_running"] = True
            
            # Step 2: Connect to MCP servers
            mcp_connected = await self._connect_mcp_servers()
            self.connection_status["mcp_connected"] = mcp_connected
            
            # Step 3: Setup LSP servers
            lsp_connected = await self._setup_lsp_servers()
            self.connection_status["lsp_connected"] = lsp_connected
            
            # Step 4: Test integration
            integration_success = await self._test_integration()
            
            if integration_success:
                self.logger.info("✅ MCP-LSP Connection established successfully")
                return True
            else:
                self.logger.error("❌ Integration test failed")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Connection failed: {e}")
            return False
    
    async def _connect_mcp_servers(self) -> bool:
        """Connect to available MCP servers"""
        try:
            self.logger.info("🔌 Connecting to MCP servers...")
            
            # Check if AgentDaf1 MCP server is running
            agentdaf_server = {
                "name": "agentdaf1",
                "url": "http://localhost:8080",
                "endpoints": {
                    "health": "/health",
                    "mcp": "/mcp",
                    "excel_read": "/api/excel/read"
                },
                "capabilities": ["excel.read", "excel.write", "excel.analyze", "dashboard.update"]
            }
            
            # Test connection
            try:
                import requests
                response = requests.get(f"{agentdaf_server['url']}{agentdaf_server['endpoints']['health']}", timeout=5)
                if response.status_code == 200:
                    self.mcp_servers["agentdaf1"] = agentdaf_server
                    self.logger.info(f"✅ Connected to AgentDaf1 MCP server")
                else:
                    self.logger.warning(f"⚠️ AgentDaf1 MCP server returned status {response.status_code}")
            except Exception as e:
                self.logger.warning(f"⚠️ Could not connect to AgentDaf1 MCP server: {e}")
            
            # Add other MCP servers
            additional_servers = {
                "sequential_thinking": {
                    "url": "http://localhost:3010",
                    "capabilities": ["analysis", "code_review", "optimization"]
                },
                "code_interpreter": {
                    "url": "http://localhost:3011",
                    "capabilities": ["execution", "debugging", "testing"]
                }
            }
            
            for name, config in additional_servers.items():
                try:
                    response = requests.get(f"{config['url']}/health", timeout=3)
                    if response.status_code == 200:
                        self.mcp_servers[name] = config
                        self.logger.info(f"✅ Connected to MCP server: {name}")
                except:
                    self.logger.debug(f"MCP server {name} not available")
            
            return len(self.mcp_servers) > 0
            
        except Exception as e:
            self.logger.error(f"❌ Failed to connect MCP servers: {e}")
            return False
    
    async def _setup_lsp_servers(self) -> bool:
        """Setup LSP servers"""
        try:
            self.logger.info("⚙️ Setting up LSP servers...")
            
            # Initialize LSP bridge
            lsp_bridge = LSPBridge(self.workspace_path)
            
            if await lsp_bridge.initialize():
                self.lsp_servers = lsp_bridge.lsp_servers
                self.logger.info(f"✅ LSP bridge initialized with {len(self.lsp_servers)} servers")
                return True
            else:
                self.logger.error("❌ Failed to initialize LSP bridge")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Failed to setup LSP servers: {e}")
            return False
    
    async def _test_integration(self) -> bool:
        """Test MCP-LSP integration"""
        try:
            self.logger.info("🧪 Testing MCP-LSP integration...")
            
            # Create a test file
            test_file = Path(self.workspace_path) / "test_integration.py"
            test_content = '''
def test_function():
    """Test function for integration testing"""
    x = 1
    y = 2
    return x + y

class TestClass:
    """Test class for integration testing"""
    def __init__(self):
        self.value = 0
    
    def method(self):
        return self.value * 2

if __name__ == "__main__":
    print(test_function())
    obj = TestClass()
    logger.info(obj.method())
'''
            
            with open(test_file, 'w') as f:
                f.write(test_content)
            
            # Test integrated analysis
            if self.interface:
                result = await self.interface.integrated_code_analysis(
                    str(test_file), 
                    "comprehensive",
                    use_mcp=len(self.mcp_servers) > 0,
                    use_lsp=len(self.lsp_servers) > 0
                )
                
                if result and not result.get("error"):
                    self.logger.info("✅ Integrated analysis test passed")
                    
                    # Cleanup
                    test_file.unlink()
                    return True
                else:
                    self.logger.error(f"❌ Integrated analysis failed: {result}")
            
            # Cleanup
            if test_file.exists():
                test_file.unlink()
            
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Integration test failed: {e}")
            return False
    
    async def start_websocket_server(self) -> bool:
        """Start WebSocket server for real-time communication"""
        try:
            if self.interface and self.connection_status["interface_running"]:
                self.logger.info(f"🌐 WebSocket server already running on port {self.connection_status['websocket_port']}")
                return True
            
            self.logger.info("🚀 Starting WebSocket server...")
            
            # The interface already starts the WebSocket server during initialization
            if self.interface:
                self.logger.info(f"✅ WebSocket server running on ws://localhost:{self.connection_status['websocket_port']}")
                return True
            else:
                self.logger.error("❌ Interface not initialized")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Failed to start WebSocket server: {e}")
            return False
    
    async def send_test_message(self, method: str, params: Dict = None) -> Dict:
        """Send a test message through the interface"""
        try:
            if not self.interface:
                return {"error": "Interface not initialized"}
            
            from tools.mcp_lsp_interface import MCPLSPMessage
            
            message = MCPLSPMessage(
                id="test",
                type="request",
                method=method,
                params=params or {}
            )
            
            response = await self.interface._process_message(message)
            return response.__dict__
            
        except Exception as e:
            return {"error": str(e)}
    
    def get_connection_status(self) -> Dict:
        """Get current connection status"""
        return {
            "timestamp": datetime.now().isoformat(),
            "connection_status": self.connection_status,
            "mcp_servers": list(self.mcp_servers.keys()),
            "lsp_servers": list(self.lsp_servers.keys()),
            "workspace_path": self.workspace_path
        }
    
    async def shutdown(self):
        """Shutdown the connection"""
        try:
            self.logger.info("🔄 Shutting down MCP-LSP Connection...")
            
            if self.interface:
                await self.interface.shutdown()
            
            self.connection_status = {
                "mcp_connected": False,
                "lsp_connected": False,
                "interface_running": False,
                "websocket_port": 8082
            }
            
            self.logger.info("✅ Shutdown complete")
            
        except Exception as e:
            self.logger.error(f"❌ Error during shutdown: {e}")

async def main():
    """Main CLI interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description="MCP-LSP Connection Script")
    parser.add_argument("--workspace", "-w", help="Workspace path", default=".")
    parser.add_argument("--connect", "-c", action="store_true", help="Establish connection")
    parser.add_argument("--status", "-s", action="store_true", help="Show connection status")
    parser.add_argument("--test", "-t", action="store_true", help="Test connection")
    parser.add_argument("--server", action="store_true", help="Start WebSocket server")
    parser.add_argument("--analyze", "-a", help="Analyze file with integrated analysis")
    parser.add_argument("--message", "-m", help="Send test message (method)")
    parser.add_argument("--params", "-p", help="Parameters for test message (JSON string)")
    
    args = parser.parse_args()
    
    connector = MCPLSPConnector(args.workspace)
    
    try:
        if args.connect or args.test or args.server or args.analyze or args.message:
            # Establish connection
            if not await connector.establish_connection():
                connector.logger.info("❌ Failed to establish connection")
                return
            
            if args.server:
                await connector.start_websocket_server()
                connector.logger.info("🚀 WebSocket server running. Press Ctrl+C to stop...")
                try:
                    while True:
                        await asyncio.sleep(1)
                except KeyboardInterrupt:
                    connector.logger.info("\n🛑 Stopping server...")
            
            elif args.test:
                print("🧪 Running integration tests...")
                success = await connector._test_integration()
                print(f"{'✅' if success else '❌'} Integration test {'passed' if success else 'failed'}")
            
            elif args.analyze:
                connector.logger.info(f"📊 Analyzing file: {args.analyze}")
                if connector.interface:
                    result = await connector.interface.integrated_code_analysis(args.analyze)
                    connector.logger.info(json.dumps(result, indent=2))
                else:
                    connector.logger.info("❌ Interface not available")
            
            elif args.message:
                params = {}
                if args.params:
                    try:
                        params = json.loads(args.params)
                    except:
                        connector.logger.info("❌ Invalid JSON parameters")
                        return
                
                connector.logger.info(f"📤 Sending message: {args.message}")
                result = await connector.send_test_message(args.message, params)
                connector.logger.info(json.dumps(result, indent=2))
            
        elif args.status:
            status = connector.get_connection_status()
            connector.logger.info(json.dumps(status, indent=2))
        
        else:
            connector.logger.info("MCP-LSP Connector")
            connector.logger.info("Use --help to see available options")
            connector.logger.info("\nQuick start:")
            print("  python mcp_lsp_connect.py --connect --test")
            connector.logger.info("  python mcp_lsp_connect.py --connect --server")
            
    finally:
        await connector.shutdown()

if __name__ == "__main__":
    asyncio.run(main())