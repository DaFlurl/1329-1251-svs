#!/usr/bin/env python3
"""
Simple MCP Server for file operations
"""

import asyncio
import json
import logging
import sys
from typing import Any, Dict, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SimpleMCPServer:
    """Simple MCP server implementation"""
    
    def __init__(self):
        """Initialize the MCP server"""
        logger.info("Starting Simple MCP Server")
        
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP requests"""
        method = request.get("method")
        params = request.get("params", {})
        
        logger.info(f"Received request: {method}")
        
        if method == "ping":
            return {"result": "pong", "status": "success"}
        elif method == "read_file":
            filename = params.get("filename")
            if not filename:
                return {"error": "filename parameter required", "status": "error"}
            
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    content = f.read()
                    return {"result": content, "status": "success", "filename": filename}
            except Exception as e:
                return {"error": str(e), "status": "error"}
        elif method == "write_file":
            filename = params.get("filename")
            content = params.get("content")
            if not filename or content is None:
                return {"error": "filename and content parameters required", "status": "error"}
            
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
                    return {"result": f"Written to {filename}", "status": "success"}
            except Exception as e:
                return {"error": str(e), "status": "error"}
        else:
            return {"error": f"Unknown method: {method}", "status": "error"}

async def main(self):
        """Main server function"""
        logger.info("Simple MCP Server running on stdio")
        
        while True:
            try:
                # Read request from stdin
                line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
                if not line:
                    break
                    
                try:
                    request = json.loads(line.strip())
                    response = await self.handle_request(request)
                    logger.info(json.dumps(response))
                except json.JSONDecodeError:
                    logger.info(json.dumps({"error": "Invalid JSON", "status": "error"}))
                except Exception as e:
                    logger.info(json.dumps({"error": str(e), "status": "error"}))
                    
            except KeyboardInterrupt:
                logger.info("Server stopped")
                break
            except Exception as e:
                logger.error(f"Server error: {e}")
                break

if __name__ == "__main__":
    server = SimpleMCPServer()
    asyncio.run(server.main())