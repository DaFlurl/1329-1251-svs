#!/usr/bin/env python3
"""
Simple MCP Server for Testing
A basic MCP server that responds to health checks and analysis requests
"""

import json
import logging
import time
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading

class SimpleMCPHandler(BaseHTTPRequestHandler):
    """Simple HTTP handler for MCP requests"""
    
    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/health':
            self._send_health_response()
        elif parsed_path.path == '/':
            self._send_info_response()
        else:
            self._send_404()
    
    def do_POST(self):
        """Handle POST requests"""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/mcp':
            self._handle_mcp_request()
        else:
            self._send_404()
    
    def _send_health_response(self):
        """Send health check response"""
        response = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "server": {
                "name": "Simple MCP Server",
                "version": "1.0.0",
                "capabilities": ["analyze", "process", "respond"],
                "endpoints": {
                    "health": "/health (GET)",
                    "info": "/ (GET)",
                    "mcp": "/mcp (POST)"
                }
            }
        }
        
        self._send_json_response(200, response)
    
    def _send_info_response(self):
        """Send server info response"""
        response = {
            "name": "Simple MCP Server",
            "version": "1.0.0",
            "description": "A simple MCP server for testing connections",
            "capabilities": ["analyze", "process", "respond"],
            "endpoints": {
                "health": "/health (GET)",
                "info": "/ (GET)",
                "mcp": "/mcp (POST)"
            }
        }
        
        self._send_json_response(200, response)
    
    def _handle_mcp_request(self):
        """Handle MCP requests"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                request_data = json.loads(post_data.decode('utf-8'))
            except json.JSONDecodeError:
                self._send_json_response(400, {"error": "Invalid JSON"})
                return
            
            # Process the request
            action = request_data.get('action', 'unknown')
            
            if action == 'analyze':
                response = self._handle_analyze(request_data)
            elif action == 'process':
                response = self._handle_process(request_data)
            else:
                response = {
                    "error": f"Unknown action: {action}",
                    "available_actions": ["analyze", "process"]
                }
            
            self._send_json_response(200, response)
            
        except Exception as e:
            self._send_json_response(500, {"error": str(e)})
    
    def _handle_analyze(self, request_data):
        """Handle analyze requests"""
        content = request_data.get('content', '')
        file_path = request_data.get('file_path', 'unknown')
        
        # Simple analysis
        lines = content.split('/n')
        analysis = {
            "file_path": file_path,
            "line_count": len(lines),
            "character_count": len(content),
            "language": self._detect_language(file_path),
            "complexity": "simple" if len(lines) < 50 else "moderate" if len(lines) < 200 else "complex",
            "has_functions": "def " in content,
            "has_classes": "class " in content,
            "has_imports": "import " in content,
            "suggestions": []
        }
        
        # Add suggestions based on content
        if analysis["has_functions"] and not analysis["has_imports"]:
            analysis["suggestions"].append("Consider adding docstrings to functions")
        
        if len(lines) > 100 and not analysis["has_classes"]:
            analysis["suggestions"].append("Consider organizing code into classes for better structure")
        
        return {
            "action": "analyze",
            "result": analysis,
            "timestamp": datetime.now().isoformat()
        }
    
    def _handle_process(self, request_data):
        """Handle process requests"""
        data = request_data.get('data', {})
        
        return {
            "action": "process",
            "result": {
                "processed": True,
                "data_received": len(str(data)),
                "processing_time": "0.001s"
            },
            "timestamp": datetime.now().isoformat()
        }
    
    def _detect_language(self, file_path):
        """Detect language from file path"""
        if file_path.endswith('.py'):
            return 'python'
        elif file_path.endswith('.js'):
            return 'javascript'
        elif file_path.endswith('.json'):
            return 'json'
        else:
            return 'unknown'
    
    def _send_json_response(self, status_code, data):
        """Send JSON response"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response_json = json.dumps(data, indent=2)
        self.wfile.write(response_json.encode('utf-8'))
    
    def _send_404(self):
        """Send 404 response"""
        self._send_json_response(404, {
            "error": "Not Found",
            "message": "The requested endpoint does not exist",
            "available_endpoints": ["/health", "/", "/mcp"]
        })
    
    def log_message(self, format, *args):
        """Override to reduce log spam"""
        pass  # Suppress default logging

class SimpleMCPServer:
    """Simple MCP Server"""
    
    def __init__(self, host='localhost', port=8080):
        self.host = host
        self.port = port
        self.server = None
        self.server_thread = None
        self.running = False
    
    def start(self):
        """Start the server"""
        try:
            self.server = HTTPServer((self.host, self.port), SimpleMCPHandler)
            self.running = True
            
            # Run in a separate thread
            self.server_thread = threading.Thread(target=self._run_server, daemon=True)
            self.server_thread.start()
            
            logger.info(f"Simple MCP Server started on http://{self.host}:{self.port}")
            logger.info("Available endpoints:")
            logger.info("  GET  /health - Health check")
            logger.info("  GET  /       - Server info")
            logger.info("  POST /mcp    - MCP requests")
            
            return True
            
        except Exception as e:
            logger.info(f"Failed to start server: {e}")
            return False
    
    def _run_server(self):
        """Run server"""
        try:
            if self.server:
                self.server.serve_forever()
        except Exception as e:
            logger.info(f"Server error: {e}")
    
    def stop(self):
        """Stop the server"""
        if self.server:
            self.running = False
            self.server.shutdown()
            self.server.server_close()
            logger.info("Simple MCP Server stopped")

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Simple MCP Server")
    parser.add_argument("--host", default="localhost", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8080, help="Port to bind to")
    parser.add_argument("--test", action="store_true", help="Test server and exit")
    
    args = parser.parse_args()
    
    server = SimpleMCPServer(args.host, args.port)
    
    if not server.start():
        return 1
    
    if args.test:
        # Test the server
        import time
        time.sleep(1)  # Give server time to start
        
        import requests
        try:
            response = requests.get(f"http://{args.host}:{args.port}/health")
            if response.status_code == 200:
                print("Server test: PASSED")
                server.stop()
                return 0
            else:
                print(f"Server test: FAILED (status {response.status_code})")
                return 1
        except Exception as e:
            print(f"Server test: FAILED ({e})")
            return 1
    
    try:
        logger.info("Press Ctrl+C to stop the server...")
        while server.running:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("/nStopping server...")
        server.stop()
    
    return 0

if __name__ == "__main__":
    exit(main())