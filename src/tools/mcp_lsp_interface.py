#!/usr/bin/env python3
"""
MCP-LSP Integration Interface for AgentDaf1.1
Provides seamless communication between MCP servers and LSP capabilities
"""

import json
import asyncio
import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import threading
from dataclasses import dataclass

# Import centralized configurations
from src.config.optional_imports import websockets, WEBSOCKETS_AVAILABLE
from src.config.logging_config import get_logger

try:
    from src.tools.lsp_bridge import LSPBridge
except ImportError:
    LSPBridge = None

try:
    from src.mcp.mcp_client import MCPClient
except ImportError:
    MCPClient = None

@dataclass
class MCPLSPMessage:
    """Message structure for MCP-LSP communication"""
    id: str
    type: str  # "request", "response", "notification"
    method: str
    params: Dict[str, Any]
    result: Optional[Any] = None
    error: Optional[Dict] = None
    timestamp: Optional[str] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()

class MCPLSPInterface:
    """Interface for MCP-LSP communication and integration"""
    
    def __init__(self, workspace_path: str = "."):
        self.workspace_path = workspace_path
        self.lsp_bridge = LSPBridge(workspace_path) if LSPBridge else None
        self.mcp_client = MCPClient() if MCPClient else None
        self.websocket_server = None
        self.active_connections = set()
        self.message_handlers = {}
        self.logger = get_logger("MCPLSPInterface")
        self.running = False
    
    async def initialize(self) -> bool:
        """Initialize MCP-LSP interface"""
        try:
            self.logger.info("Initializing MCP-LSP Interface...")
            
            # Initialize LSP bridge
            if self.lsp_bridge and not await self.lsp_bridge.initialize():
                self.logger.error("Failed to initialize LSP bridge")
                return False
            
            # Initialize MCP client
            if self.mcp_client and not await self.mcp_client.initialize():
                self.logger.error("Failed to initialize MCP client")
                return False
            
            # Register message handlers
            self._register_message_handlers()
            
            # Start WebSocket server for real-time communication
            await self._start_websocket_server()
            
            self.running = True
            self.logger.info("MCP-LSP Interface initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize MCP-LSP Interface: {e}")
            return False
    
    def _register_message_handlers(self):
        """Register message handlers for different operations"""
        self.message_handlers = {
            "analyze_code": self._handle_analyze_code,
            "get_completions": self._handle_get_completions,
            "get_diagnostics": self._handle_get_diagnostics,
            "format_code": self._handle_format_code,
            "mcp_execute": self._handle_mcp_execute,
            "lsp_operation": self._handle_lsp_operation,
            "integrated_analysis": self._handle_integrated_analysis
        }
    
    async def _start_websocket_server(self):
        """Start WebSocket server for real-time communication"""
        try:
            if not WEBSOCKETS_AVAILABLE:
                raise ImportError("websockets library not available")
            
            async def handle_client(websocket, path):
                self.active_connections.add(websocket)
                self.logger.info(f"Client connected: {websocket.remote_address}")
                
                try:
                    async for message in websocket:
                        await self._handle_websocket_message(websocket, message)
                except websockets.exceptions.ConnectionClosed:
                    self.logger.info(f"Client disconnected: {websocket.remote_address}")
                finally:
                    self.active_connections.discard(websocket)
            
            # Start WebSocket server
            self.websocket_server = await websockets.serve(
                handle_client,
                "localhost",
                8082,
                ping_interval=20,
                ping_timeout=10
            )
            
            self.logger.info("WebSocket server started on ws://localhost:8082")
            
        except Exception as e:
            self.logger.error(f"Failed to start WebSocket server: {e}")
    
    async def _handle_websocket_message(self, websocket, message: str):
        """Handle incoming WebSocket messages"""
        try:
            data = json.loads(message)
            msg = MCPLSPMessage(**data)
            
            self.logger.info(f"Received message: {msg.method}")
            
            # Process message
            response = await self._process_message(msg)
            
            # Send response
            await websocket.send(json.dumps(response))
            
        except json.JSONDecodeError:
            error_response = MCPLSPMessage(
                id="error",
                type="response",
                method="error",
                params={},
                error={"code": -32700, "message": "Parse error"}
            )
            await websocket.send(json.dumps(error_response.__dict__))
        except Exception as e:
            self.logger.error(f"Error handling WebSocket message: {e}")
    
    async def _process_message(self, msg: MCPLSPMessage) -> MCPLSPMessage:
        """Process incoming message"""
        try:
            handler = self.message_handlers.get(msg.method)
            if handler:
                result = await handler(msg.params)
                return MCPLSPMessage(
                    id=msg.id,
                    type="response",
                    method=msg.method,
                    params={},
                    result=result
                )
            else:
                return MCPLSPMessage(
                    id=msg.id,
                    type="response",
                    method=msg.method,
                    params={},
                    error={"code": -32601, "message": "Method not found"}
                )
        except Exception as e:
            self.logger.error(f"Error processing message: {e}")
            return MCPLSPMessage(
                id=msg.id,
                type="response",
                method=msg.method,
                params={},
                error={"code": -32603, "message": str(e)}
            )
    
    async def _handle_analyze_code(self, params: Dict) -> Dict:
        """Handle code analysis request"""
        try:
            file_path = params.get("file_path")
            analysis_type = params.get("analysis_type", "comprehensive")
            use_mcp = params.get("use_mcp", True)
            use_lsp = params.get("use_lsp", True)
            
            if not file_path:
                return {"error": "file_path is required"}
            
            # Perform integrated analysis
            result = await self.integrated_code_analysis(
                file_path, analysis_type, use_mcp, use_lsp
            )
            
            return result
            
        except Exception as e:
            return {"error": str(e)}
    
    async def _handle_get_completions(self, params: Dict) -> Dict:
        """Handle code completion request"""
        try:
            file_path = params.get("file_path")
            line = params.get("line")
            column = params.get("column")
            
            if not all([file_path, line is not None, column is not None]):
                return {"error": "file_path, line, and column are required"}
            
            completions = await self.lsp_bridge.get_completions(file_path, line, column)
            
            # Enhance with MCP suggestions if available
            mcp_suggestions = await self._get_mcp_completion_suggestions(file_path, line, column)
            
            return {
                "completions": completions,
                "mcp_suggestions": mcp_suggestions,
                "enhanced": len(mcp_suggestions) > 0
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    async def _handle_get_diagnostics(self, params: Dict) -> Dict:
        """Handle diagnostics request"""
        try:
            file_path = params.get("file_path")
            
            if not file_path:
                return {"error": "file_path is required"}
            
            diagnostics = await self.lsp_bridge.get_diagnostics(file_path)
            
            # Enhance with MCP analysis
            mcp_analysis = await self._get_mcp_diagnostic_analysis(file_path)
            
            return {
                "diagnostics": diagnostics,
                "mcp_analysis": mcp_analysis,
                "total_issues": len(diagnostics)
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    async def _handle_format_code(self, params: Dict) -> Dict:
        """Handle code formatting request"""
        try:
            file_path = params.get("file_path")
            
            if not file_path:
                return {"error": "file_path is required"}
            
            result = await self.lsp_bridge.format_code(file_path)
            
            # Get MCP suggestions for improvements
            if result.get("success"):
                mcp_suggestions = await self._get_mcp_formatting_suggestions(file_path)
                result["mcp_suggestions"] = mcp_suggestions
            
            return result
            
        except Exception as e:
            return {"error": str(e)}
    
    async def _handle_mcp_execute(self, params: Dict) -> Dict:
        """Handle MCP execution request"""
        try:
            server_name = params.get("server_name")
            command = params.get("command")
            args = params.get("args", {})
            
            if not all([server_name, command]):
                return {"error": "server_name and command are required"}
            
            result = await self.mcp_client.execute_command(server_name, command, args)
            
            return result
            
        except Exception as e:
            return {"error": str(e)}
    
    async def _handle_lsp_operation(self, params: Dict) -> Dict:
        """Handle LSP operation request"""
        try:
            operation = params.get("operation")
            file_path = params.get("file_path")
            args = params.get("args", {})
            
            if not all([operation, file_path]):
                return {"error": "operation and file_path are required"}
            
            if operation == "goto_definition":
                result = await self._lsp_goto_definition(file_path, args.get("line", 0), args.get("column", 0))
            elif operation == "find_references":
                result = await self._lsp_find_references(file_path, args.get("line", 0), args.get("column", 0))
            elif operation == "hover":
                result = await self._lsp_hover(file_path, args.get("line", 0), args.get("column", 0))
            else:
                return {"error": f"Unknown LSP operation: {operation}"}
            
            return result
            
        except Exception as e:
            return {"error": str(e)}
    
    async def _handle_integrated_analysis(self, params: Dict) -> Dict:
        """Handle integrated analysis request"""
        try:
            file_path = params.get("file_path")
            analysis_options = params.get("options", {})
            
            if not file_path:
                return {"error": "file_path is required"}
            
            result = await self.integrated_code_analysis(
                file_path,
                analysis_options.get("type", "comprehensive"),
                analysis_options.get("use_mcp", True),
                analysis_options.get("use_lsp", True),
                analysis_options
            )
            
            return result
            
        except Exception as e:
            return {"error": str(e)}
    
    async def integrated_code_analysis(
        self,
        file_path: str,
        analysis_type: str = "comprehensive",
        use_mcp: bool = True,
        use_lsp: bool = True,
        options: Dict = None
    ) -> Dict:
        """Perform integrated code analysis using both MCP and LSP"""
        try:
            options = options or {}
            
            result = {
                "file_path": file_path,
                "analysis_type": analysis_type,
                "timestamp": datetime.now().isoformat(),
                "lsp_analysis": None,
                "mcp_analysis": None,
                "integrated_insights": [],
                "recommendations": []
            }
            
            # LSP Analysis
            if use_lsp:
                lsp_result = await self.lsp_bridge.analyze_code(file_path, analysis_type)
                result["lsp_analysis"] = lsp_result
            
            # MCP Analysis
            if use_mcp:
                mcp_result = await self._perform_mcp_analysis(file_path, analysis_type, options)
                result["mcp_analysis"] = mcp_result
            
            # Generate integrated insights
            result["integrated_insights"] = await self._generate_integrated_insights(
                result["lsp_analysis"], result["mcp_analysis"]
            )
            
            # Generate recommendations
            result["recommendations"] = await self._generate_recommendations(
                result["lsp_analysis"], result["mcp_analysis"]
            )
            
            return result
            
        except Exception as e:
            return {"error": str(e)}
    
    async def _perform_mcp_analysis(self, file_path: str, analysis_type: str, options: Dict) -> Dict:
        """Perform MCP-based analysis"""
        try:
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Use sequential thinking for code analysis
            analysis_prompt = f"""
            Analyze this code file: {file_path}
            
            Analysis type: {analysis_type}
            Options: {json.dumps(options, indent=2)}
            
            Content:
            {content}
            
            Please provide:
            1. Code quality assessment (1-10 scale)
            2. Security vulnerabilities
            3. Performance bottlenecks
            4. Best practices violations
            5. Improvement suggestions
            6. Complexity analysis
            """
            
            result = None
            if self.mcp_client:
                result = await self.mcp_client.sequential_thinking(analysis_prompt)
            else:
                result = {"error": "MCP client not available"}
            
            return {
                "server": "sequential_thinking",
                "analysis": result,
                "file_path": file_path,
                "analysis_type": analysis_type
            }
            
        except Exception as e:
            return {"error": f"MCP analysis failed: {e}"}
    
    async def _generate_integrated_insights(self, lsp_analysis: Dict, mcp_analysis: Dict) -> List[Dict]:
        """Generate integrated insights from both LSP and MCP analysis"""
        insights = []
        
        try:
            # Combine LSP diagnostics with MCP analysis
            if lsp_analysis and lsp_analysis.get("lsp_analysis", {}).get("results", {}).get("diagnostics"):
                lsp_diagnostics = lsp_analysis["lsp_analysis"]["results"]["diagnostics"]
                
                for diagnostic in lsp_diagnostics:
                    insight = {
                        "type": "lsp_diagnostic",
                        "severity": diagnostic.get("severity", "info"),
                        "message": diagnostic.get("message", ""),
                        "line": diagnostic.get("line", 0),
                        "source": "lsp"
                    }
                    insights.append(insight)
            
            # Add MCP insights
            if mcp_analysis and not mcp_analysis.get("error"):
                mcp_insights = {
                    "type": "mcp_analysis",
                    "severity": "info",
                    "message": "MCP analysis completed",
                    "analysis": mcp_analysis.get("analysis", {}),
                    "source": "mcp"
                }
                insights.append(mcp_insights)
            
            return insights
            
        except Exception as e:
            self.logger.error(f"Error generating integrated insights: {e}")
            return []
    
    async def _generate_recommendations(self, lsp_analysis: Dict, mcp_analysis: Dict) -> List[Dict]:
        """Generate recommendations based on analysis"""
        recommendations = []
        
        try:
            # LSP-based recommendations
            if lsp_analysis and lsp_analysis.get("lsp_analysis", {}).get("results", {}).get("diagnostics"):
                diagnostics = lsp_analysis["lsp_analysis"]["results"]["diagnostics"]
                
                # Group by severity
                errors = [d for d in diagnostics if d.get("severity") == "error"]
                warnings = [d for d in diagnostics if d.get("severity") == "warning"]
                
                if errors:
                    recommendations.append({
                        "priority": "high",
                        "type": "fix_errors",
                        "message": f"Fix {len(errors)} critical error(s)",
                        "count": len(errors)
                    })
                
                if warnings:
                    recommendations.append({
                        "priority": "medium",
                        "type": "address_warnings",
                        "message": f"Address {len(warnings)} warning(s)",
                        "count": len(warnings)
                    })
            
            # MCP-based recommendations
            if mcp_analysis and not mcp_analysis.get("error"):
                recommendations.append({
                    "priority": "low",
                    "type": "mcp_suggestions",
                    "message": "Review MCP analysis for optimization opportunities",
                    "analysis_available": True
                })
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Error generating recommendations: {e}")
            return []
    
    async def _get_mcp_completion_suggestions(self, file_path: str, line: int, column: int) -> List[Dict]:
        """Get MCP-based completion suggestions"""
        try:
            # This would integrate with MCP servers for intelligent completions
            # For now, return empty list
            return []
        except Exception as e:
            self.logger.error(f"Error getting MCP completion suggestions: {e}")
            return []
    
    async def _get_mcp_diagnostic_analysis(self, file_path: str) -> Dict:
        """Get MCP-based diagnostic analysis"""
        try:
            # This would use MCP servers for deeper analysis
            return {"status": "MCP diagnostic analysis not implemented"}
        except Exception as e:
            self.logger.error(f"Error getting MCP diagnostic analysis: {e}")
            return {"error": str(e)}
    
    async def _get_mcp_formatting_suggestions(self, file_path: str) -> List[Dict]:
        """Get MCP-based formatting suggestions"""
        try:
            # This would use MCP servers for formatting suggestions
            return []
        except Exception as e:
            self.logger.error(f"Error getting MCP formatting suggestions: {e}")
            return []
    
    async def _lsp_goto_definition(self, file_path: str, line: int, column: int) -> Dict:
        """LSP go to definition"""
        try:
            # This would implement actual LSP goto definition
            return {"message": "Goto definition not implemented"}
        except Exception as e:
            return {"error": str(e)}
    
    async def _lsp_find_references(self, file_path: str, line: int, column: int) -> Dict:
        """LSP find references"""
        try:
            # This would implement actual LSP find references
            return {"message": "Find references not implemented"}
        except Exception as e:
            return {"error": str(e)}
    
    async def _lsp_hover(self, file_path: str, line: int, column: int) -> Dict:
        """LSP hover"""
        try:
            # This would implement actual LSP hover
            return {"message": "Hover not implemented"}
        except Exception as e:
            return {"error": str(e)}
    
    async def broadcast_notification(self, method: str, params: Dict):
        """Broadcast notification to all connected clients"""
        if not self.active_connections:
            return
        
        notification = MCPLSPMessage(
            id="notification",
            type="notification",
            method=method,
            params=params
        )
        
        message = json.dumps(notification.__dict__)
        
        # Send to all connected clients
        disconnected = set()
        for websocket in self.active_connections:
            try:
                await websocket.send(message)
            except Exception as e:
                self.logger.error(f"Error sending notification: {e}")
                disconnected.add(websocket)
        
        # Remove disconnected clients
        self.active_connections -= disconnected
    
    async def shutdown(self):
        """Shutdown MCP-LSP interface"""
        try:
            self.logger.info("Shutting down MCP-LSP Interface...")
            
            self.running = False
            
            # Close WebSocket server
            if self.websocket_server:
                self.websocket_server.close()
                await self.websocket_server.wait_closed()
            
            # Close active connections
            for websocket in self.active_connections.copy():
                try:
                    websocket.close()
                except:
                    pass
            self.active_connections.clear()
            
            # Shutdown LSP bridge
            await self.lsp_bridge.shutdown()
            
            # Shutdown MCP client
            await self.mcp_client.shutdown()
            
            self.logger.info("MCP-LSP Interface shutdown complete")
            
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")

# CLI Interface
async def main():
    """CLI interface for MCP-LSP Interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description="MCP-LSP Interface for AgentDaf1.1")
    parser.add_argument("--workspace", "-w", help="Workspace path", default=".")
    parser.add_argument("--analyze", "-a", help="Analyze file with integrated analysis")
    parser.add_argument("--server", "-s", action="store_true", help="Start WebSocket server")
    parser.add_argument("--test", "-t", action="store_true", help="Test MCP-LSP integration")
    
    args = parser.parse_args()
    
    interface = MCPLSPInterface(args.workspace)
    
    if not await interface.initialize():
        logger.info("❌ Failed to initialize MCP-LSP Interface")
        return
    
    try:
        if args.analyze:
            result = await interface.integrated_code_analysis(args.analyze)
            logger.info(json.dumps(result, indent=2))
        elif args.server:
            logger.info("🚀 MCP-LSP WebSocket server running on ws://localhost:8082")
            logger.info("Press Ctrl+C to stop...")
            
            # Keep server running
            while interface.running:
                await asyncio.sleep(1)
        elif args.test:
            logger.info("🧪 Testing MCP-LSP Integration...")
            
            # Test with a sample file
            test_file = "test_mcp_lsp_sample.py"
            with open(test_file, 'w') as f:
                f.write("""
def test_function():
    x = 1
    y = 2
    return x + y

class TestClass:
    def __init__(self):
        self.value = 0
    
    def method(self):
        return self.value * 2
""")
            
            result = await interface.integrated_code_analysis(test_file)
            logger.info("Integrated analysis result:")
            logger.info(json.dumps(result, indent=2))
            
            # Cleanup
            import os
            os.remove(test_file)
            print("✅ MCP-LSP integration test completed")
        else:
            logger.info("MCP-LSP Interface initialized. Use --help for options.")
            
    finally:
        await interface.shutdown()

if __name__ == "__main__":
    asyncio.run(main())