#!/usr/bin/env python3
"""
Simple MCP-LSP Connection Test
Tests the basic connectivity between MCP and LSP components
"""

import asyncio
import json
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

async def test_mcp_connection():
    """Test MCP server connection"""
    print("🔌 Testing MCP Connection...")
    
    try:
        import requests
        
        # Test AgentDaf1 MCP server
        response = requests.get("http://localhost:8080/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ AgentDaf1 MCP Server: {data.get('status', 'unknown')}")
            print(f"   Capabilities: {data.get('server', {}).get('capabilities', [])}")
            return True
        else:
            print(f"❌ AgentDaf1 MCP Server returned {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ MCP Connection failed: {e}")
        return False

async def test_lsp_bridge():
    """Test LSP bridge functionality"""
    print("⚙️ Testing LSP Bridge...")
    
    try:
        # Try to import and initialize LSP bridge
        from tools.lsp_bridge import LSPBridge
        
        bridge = LSPBridge(".")
        success = await bridge.initialize()
        
        if success:
            print(f"✅ LSP Bridge initialized with {len(bridge.lsp_servers)} servers")
            for name, server in bridge.lsp_servers.items():
                print(f"   - {name}: {server['config'].get('language', 'unknown')}")
            await bridge.shutdown()
            return True
        else:
            print("❌ LSP Bridge initialization failed")
            return False
            
    except Exception as e:
        print(f"❌ LSP Bridge test failed: {e}")
        return False

async def test_mcp_client():
    """Test MCP client functionality"""
    print("📡 Testing MCP Client...")
    
    try:
        from mcp.mcp_client import MCPClient
        
        client = MCPClient()
        success = await client.initialize()
        
        if success:
            print(f"✅ MCP Client initialized with {len(client.servers)} servers")
            for name in client.servers.keys():
                print(f"   - {name}")
            
            # Test sequential thinking if available
            if "sequential_thinking" in client.servers:
                result = await client.sequential_thinking("Test message: 2+2=?")
                if not result.get("error"):
                    print("✅ Sequential thinking test passed")
                else:
                    print(f"⚠️ Sequential thinking test: {result.get('error')}")
            
            await client.shutdown()
            return True
        else:
            print("❌ MCP Client initialization failed")
            return False
            
    except Exception as e:
        print(f"❌ MCP Client test failed: {e}")
        return False

async def test_integrated_interface():
    """Test integrated MCP-LSP interface"""
    print("🔗 Testing Integrated Interface...")
    
    try:
        from tools.mcp_lsp_interface import MCPLSPInterface
        
        interface = MCPLSPInterface(".")
        success = await interface.initialize()
        
        if success:
            print("✅ MCP-LSP Interface initialized")
            
            # Create a test file
            test_file = "test_mcp_lsp.py"
            with open(test_file, 'w') as f:
                f.write("""
def hello_world():
    return "Hello, World!"

class TestClass:
    def __init__(self):
        self.value = 42
    
    def get_value(self):
        return self.value
""")
            
            # Test integrated analysis
            result = await interface.integrated_code_analysis(test_file)
            
            if not result.get("error"):
                print("✅ Integrated analysis test passed")
                print(f"   File: {result.get('file_path')}")
                print(f"   LSP Analysis: {'✅' if result.get('lsp_analysis') else '❌'}")
                print(f"   MCP Analysis: {'✅' if result.get('mcp_analysis') else '❌'}")
                print(f"   Insights: {len(result.get('integrated_insights', []))}")
                print(f"   Recommendations: {len(result.get('recommendations', []))}")
            else:
                print(f"❌ Integrated analysis failed: {result.get('error')}")
            
            # Cleanup
            if os.path.exists(test_file):
                os.remove(test_file)
            
            await interface.shutdown()
            return not result.get("error")
        else:
            print("❌ MCP-LSP Interface initialization failed")
            return False
            
    except Exception as e:
        print(f"❌ Integrated Interface test failed: {e}")
        return False

async def main():
    """Main test function"""
    print("🧪 MCP-LSP Connection Test Suite")
    print("=" * 50)
    
    tests = [
        ("MCP Connection", test_mcp_connection),
        ("LSP Bridge", test_lsp_bridge),
        ("MCP Client", test_mcp_client),
        ("Integrated Interface", test_integrated_interface)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"/n📋 Running: {test_name}")
        try:
            result = await test_func()
            results[test_name] = result
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results[test_name] = False
    
    # Summary
    print("/n" + "=" * 50)
    print("📊 Test Results Summary:")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"/n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! MCP-LSP connection is working.")
        return True
    else:
        print("⚠️ Some tests failed. Check the logs above for details.")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)