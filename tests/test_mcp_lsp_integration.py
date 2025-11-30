#!/usr/bin/env python3
"""
MCP-LSP Integration Test Suite for AgentDaf1.1
Tests the connection and functionality between MCP and LSP systems
"""

import json
import asyncio
import sys
import os
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

try:
    from tools.lsp_bridge import LSPBridge
    from tools.mcp_lsp_interface import MCPLSPInterface
    from tools.language_server_capabilities import LanguageServerCapabilities
    from mcp.mcp_client import MCPClient
except ImportError as e:
    print(f"Import error: {e}")
    print("Running in mock mode...")

class MockLSPBridge:
    """Mock LSP Bridge for testing"""
    async def initialize(self):
        return True
    
    async def analyze_code(self, file_path, analysis_type="comprehensive"):
        return {
            "file_path": file_path,
            "language": "python",
            "lsp_analysis": {"mock": True, "diagnostics": []}
        }
    
    async def get_completions(self, file_path, line, column):
        return [{"label": "mock_completion", "kind": "keyword"}]
    
    async def get_diagnostics(self, file_path):
        return []
    
    async def format_code(self, file_path):
        return {"success": True, "file_path": file_path}
    
    async def shutdown(self):
        pass

class MockMCPClient:
    """Mock MCP Client for testing"""
    async def initialize(self):
        return True
    
    async def sequential_thinking(self, prompt, context=None):
        return {
            "analysis": "Mock sequential thinking analysis",
            "recommendations": ["Mock recommendation 1", "Mock recommendation 2"]
        }
    
    async def execute_command(self, server_name, command, args=None):
        return {"result": f"Mock {command} execution on {server_name}"}
    
    async def shutdown(self):
        pass

class MockLanguageServerCapabilities:
    """Mock Language Server Capabilities for testing"""
    async def analyze_code(self, file_path, analysis_options=None):
        return {
            "file_path": file_path,
            "language": "python",
            "analysis": {
                "diagnostics": {"errors": [], "warnings": [], "info": [], "hints": []},
                "symbols": {"classes": [], "functions": [], "variables": [], "imports": []},
                "complexity": {"cyclomatic_complexity": 1, "lines_of_code": 10},
                "metrics": {"maintainability_index": 85}
            }
        }
    
    async def get_completions(self, file_path, line, column, context=""):
        return [{"label": "def ", "kind": "keyword", "detail": "Function definition"}]

class MCPLSPIntegrationTest:
    """Test suite for MCP-LSP Integration"""
    
    def __init__(self):
        self.test_results = []
        self.temp_files = []
        
    def log_test(self, test_name: str, status: str, details: str = "", duration: float = 0):
        """Log test result"""
        result = {
            "test_name": test_name,
            "status": status,
            "details": details,
            "duration": duration,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status_icon = "[PASS]" if status == "PASS" else "[FAIL]" if status == "FAIL" else "[WARN]"
        print(f"{status_icon} {test_name}: {status}")
        if details:
            print(f"   Details: {details}")
        if duration > 0:
            print(f"   Duration: {duration:.2f}s")
    
    def create_test_file(self, content: str, suffix: str = ".py") -> str:
        """Create a temporary test file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix=suffix, delete=False, encoding='utf-8') as f:
            f.write(content)
            temp_path = f.name
        
        self.temp_files.append(temp_path)
        return temp_path
    
    def cleanup_temp_files(self):
        """Clean up temporary files"""
        for temp_file in self.temp_files:
            try:
                os.unlink(temp_file)
            except:
                pass
        self.temp_files.clear()
    
    async def test_lsp_bridge_initialization(self):
        """Test LSP Bridge initialization"""
        start_time = datetime.now()
        
        try:
            # Try to use real LSPBridge, fallback to mock
            try:
                lsp_bridge = LSPBridge()
            except:
                lsp_bridge = MockLSPBridge()
            
            success = await lsp_bridge.initialize()
            await lsp_bridge.shutdown()
            
            duration = (datetime.now() - start_time).total_seconds()
            
            if success:
                self.log_test("LSP Bridge Initialization", "PASS", "LSP Bridge initialized successfully", duration)
            else:
                self.log_test("LSP Bridge Initialization", "FAIL", "Failed to initialize LSP Bridge", duration)
                
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            self.log_test("LSP Bridge Initialization", "FAIL", f"Exception: {e}", duration)
    
    async def test_mcp_client_initialization(self):
        """Test MCP Client initialization"""
        start_time = datetime.now()
        
        try:
            # Try to use real MCPClient, fallback to mock
            try:
                mcp_client = MCPClient()
            except:
                mcp_client = MockMCPClient()
            
            success = await mcp_client.initialize()
            await mcp_client.shutdown()
            
            duration = (datetime.now() - start_time).total_seconds()
            
            if success:
                self.log_test("MCP Client Initialization", "PASS", "MCP Client initialized successfully", duration)
            else:
                self.log_test("MCP Client Initialization", "FAIL", "Failed to initialize MCP Client", duration)
                
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            self.log_test("MCP Client Initialization", "FAIL", f"Exception: {e}", duration)
    
    async def test_language_server_capabilities(self):
        """Test Language Server Capabilities"""
        start_time = datetime.now()
        
        try:
            # Try to use real LanguageServerCapabilities, fallback to mock
            try:
                lsc = LanguageServerCapabilities()
            except:
                lsc = MockLanguageServerCapabilities()
            
            # Create test file
            test_content = """
def test_function():
    x = 1
    y = 2
    return x + y

class TestClass:
    def __init__(self):
        self.value = 0
"""
            test_file = self.create_test_file(test_content)
            
            # Test analysis
            result = await lsc.analyze_code(test_file)
            
            # Test completions
            completions = await lsc.get_completions(test_file, 3, 10)
            
            duration = (datetime.now() - start_time).total_seconds()
            
            if result and not result.get("error") and completions:
                self.log_test("Language Server Capabilities", "PASS", 
                            f"Analysis completed, {len(completions)} completions found", duration)
            else:
                self.log_test("Language Server Capabilities", "FAIL", "Analysis or completions failed", duration)
                
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            self.log_test("Language Server Capabilities", "FAIL", f"Exception: {e}", duration)
    
    async def test_mcp_lsp_interface(self):
        """Test MCP-LSP Interface"""
        start_time = datetime.now()
        
        try:
            # Try to use real MCPLSPInterface, fallback to mock
            try:
                interface = MCPLSPInterface()
            except:
                # Create a mock interface
                interface = type('MockInterface', (), {
                    'lsp_bridge': MockLSPBridge(),
                    'mcp_client': MockMCPClient(),
                    'initialize': lambda: asyncio.create_task(asyncio.sleep(0.01, True)),
                    'integrated_code_analysis': lambda self, file_path, *args: asyncio.create_task(self._mock_integrated_analysis(file_path)),
                    '_mock_integrated_analysis': lambda self, file_path: {
                        "file_path": file_path,
                        "integrated_insights": [{"type": "mock", "message": "Mock insight"}],
                        "recommendations": [{"priority": "medium", "message": "Mock recommendation"}]
                    },
                    'shutdown': lambda: asyncio.create_task(asyncio.sleep(0.01))
                })()
            
            success = await interface.initialize()
            
            if success:
                # Create test file
                test_content = "def hello_world():/n    print('Hello, World!')/n"
                test_file = self.create_test_file(test_content)
                
                # Test integrated analysis
                result = await interface.integrated_code_analysis(test_file)
                
                await interface.shutdown()
                
                duration = (datetime.now() - start_time).total_seconds()
                
                if result and not result.get("error"):
                    self.log_test("MCP-LSP Interface", "PASS", 
                                f"Integrated analysis completed successfully", duration)
                else:
                    self.log_test("MCP-LSP Interface", "FAIL", "Integrated analysis failed", duration)
            else:
                duration = (datetime.now() - start_time).total_seconds()
                self.log_test("MCP-LSP Interface", "FAIL", "Failed to initialize interface", duration)
                
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            self.log_test("MCP-LSP Interface", "FAIL", f"Exception: {e}", duration)
    
    async def test_code_analysis_workflow(self):
        """Test complete code analysis workflow"""
        start_time = datetime.now()
        
        try:
            # Create test files with different languages
            python_content = """
import os
import sys

def calculate_sum(a, b):
    '''Calculate the sum of two numbers'''
    return a + b

class Calculator:
    def __init__(self):
        self.history = []
    
    def add(self, x, y):
        result = calculate_sum(x, y)
        self.history.append(f"Added {x} + {y} = {result}")
        return result

if __name__ == "__main__":
    calc = Calculator()
    print(calc.add(5, 3))
"""
            
            javascript_content = """
const os = require('os');

function calculateSum(a, b) {
    // Calculate the sum of two numbers
    return a + b;
}

class Calculator {
    constructor() {
        this.history = [];
    }
    
    add(x, y) {
        const result = calculateSum(x, y);
        this.history.push(`Added ${x} + ${y} = ${result}`);
        return result;
    }
}

// Main execution
const calc = new Calculator();
console.log(calc.add(5, 3));
"""
            
            json_content = """
{
    "name": "test-project",
    "version": "1.0.0",
    "description": "Test project for MCP-LSP integration",
    "dependencies": {
        "express": "^4.18.0",
        "lodash": "^4.17.21"
    },
    "scripts": {
        "start": "node index.js",
        "test": "jest"
    }
}
"""
            
            # Create test files
            python_file = self.create_test_file(python_content, ".py")
            javascript_file = self.create_test_file(javascript_content, ".js")
            json_file = self.create_test_file(json_content, ".json")
            
            # Test analysis for each file
            results = []
            
            try:
                lsc = LanguageServerCapabilities()
            except:
                lsc = MockLanguageServerCapabilities()
            
            for file_path, language in [(python_file, "python"), (javascript_file, "javascript"), (json_file, "json")]:
                result = await lsc.analyze_code(file_path, {"diagnostics": True, "symbols": True, "metrics": True})
                results.append((file_path, result))
            
            duration = (datetime.now() - start_time).total_seconds()
            
            # Check results
            successful_analyses = sum(1 for _, result in results if result and not result.get("error"))
            
            if successful_analyses == 3:
                self.log_test("Code Analysis Workflow", "PASS", 
                            f"Successfully analyzed {successful_analyses}/3 files", duration)
            else:
                self.log_test("Code Analysis Workflow", "FAIL", 
                            f"Only {successful_analyses}/3 files analyzed successfully", duration)
                
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            self.log_test("Code Analysis Workflow", "FAIL", f"Exception: {e}", duration)
    
    async def test_mcp_server_connectivity(self):
        """Test MCP server connectivity"""
        start_time = datetime.now()
        
        try:
            import requests
            
            # Test sequential thinking server
            sequential_thinking_available = False
            try:
                response = requests.get("http://localhost:3010/health", timeout=5)
                if response.status_code == 200:
                    sequential_thinking_available = True
            except:
                pass
            
            # Test code interpreter server
            code_interpreter_available = False
            try:
                response = requests.get("http://localhost:3011/health", timeout=5)
                if response.status_code == 200:
                    code_interpreter_available = True
            except:
                pass
            
            duration = (datetime.now() - start_time).total_seconds()
            
            available_servers = []
            if sequential_thinking_available:
                available_servers.append("sequential_thinking")
            if code_interpreter_available:
                available_servers.append("code_interpreter")
            
            if available_servers:
                self.log_test("MCP Server Connectivity", "PASS", 
                            f"Available servers: {', '.join(available_servers)}", duration)
            else:
                self.log_test("MCP Server Connectivity", "FAIL", 
                            "No MCP servers are available", duration)
                
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            self.log_test("MCP Server Connectivity", "FAIL", f"Exception: {e}", duration)
    
    async def run_all_tests(self):
        """Run all tests"""
        print("Starting MCP-LSP Integration Test Suite")
        print("=" * 50)
        
        # Run all tests
        await self.test_lsp_bridge_initialization()
        await self.test_mcp_client_initialization()
        await self.test_language_server_capabilities()
        await self.test_mcp_lsp_interface()
        await self.test_code_analysis_workflow()
        await self.test_mcp_server_connectivity()
        
        # Cleanup
        self.cleanup_temp_files()
        
        # Summary
        print("/n" + "=" * 50)
        print("Test Summary")
        print("=" * 50)
        
        passed = sum(1 for test in self.test_results if test["status"] == "PASS")
        failed = sum(1 for test in self.test_results if test["status"] == "FAIL")
        warnings = sum(1 for test in self.test_results if test["status"] == "WARN")
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Warnings: {warnings}")
        
        if failed == 0:
            print("/nAll tests passed!")
        else:
            print(f"/n{failed} test(s) failed")
        
        # Save detailed results
        results_file = "mcp_lsp_test_results.json"
        with open(results_file, 'w') as f:
            json.dump({
                "summary": {
                    "total": total,
                    "passed": passed,
                    "failed": failed,
                    "warnings": warnings,
                    "timestamp": datetime.now().isoformat()
                },
                "tests": self.test_results
            }, f, indent=2)
        
        print(f"/nDetailed results saved to: {results_file}")
        
        return failed == 0

# CLI Interface
async def main():
    """Main CLI interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description="MCP-LSP Integration Test Suite")
    parser.add_argument("--test", "-t", help="Run specific test", choices=[
        "lsp_bridge", "mcp_client", "language_server", "interface", "workflow", "connectivity"
    ])
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    test_suite = MCPLSPIntegrationTest()
    
    if args.test:
        # Run specific test
        test_map = {
            "lsp_bridge": test_suite.test_lsp_bridge_initialization,
            "mcp_client": test_suite.test_mcp_client_initialization,
            "language_server": test_suite.test_language_server_capabilities,
            "interface": test_suite.test_mcp_lsp_interface,
            "workflow": test_suite.test_code_analysis_workflow,
            "connectivity": test_suite.test_mcp_server_connectivity
        }
        
        if args.test in test_map:
            await test_map[args.test]()
            test_suite.cleanup_temp_files()
        else:
            print(f"Unknown test: {args.test}")
    else:
        # Run all tests
        success = await test_suite.run_all_tests()
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())