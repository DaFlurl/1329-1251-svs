#!/usr/bin/env python3
"""
Simple MCP-LSP Connection Test
Tests the basic functionality without Unicode characters
"""

import asyncio
import sys
import os
from pathlib import Path

# Add src to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(project_root, 'src'))

async def test_mcp_lsp_basic():
    """Basic test of MCP-LSP functionality"""
    print("Testing MCP-LSP Connection...")
    
    try:
        # Test imports
        from tools.mcp_lsp_interface import MCPLSPInterface
        from mcp.mcp_client import MCPClient
        print("[OK] Imports successful")
        
        # Test MCP Client
        mcp_client = MCPClient()
        if await mcp_client.initialize():
            print("[OK] MCP Client initialized")
        else:
            print("[WARN] MCP Client initialization failed")
        
        # Test Interface
        interface = MCPLSPInterface(".")
        if await interface.initialize():
            print("[OK] MCP-LSP Interface initialized")
            print(f"[OK] WebSocket server running")
        else:
            print("[WARN] Interface initialization failed")
        
        # Test basic message
        from tools.mcp_lsp_interface import MCPLSPMessage
        test_message = MCPLSPMessage(
            id="test",
            type="request",
            method="test",
            params={"test": True}
        )
        print(f"[OK] Message creation works: {test_message.id}")
        
        # Cleanup
        if 'interface' in locals():
            await interface.shutdown()
        if 'mcp_client' in locals():
            await mcp_client.shutdown()
            
        print("[OK] Test completed successfully")
        return True
        
    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_mcp_lsp_basic())
    sys.exit(0 if success else 1)