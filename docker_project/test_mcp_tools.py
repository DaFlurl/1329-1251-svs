#!/usr/bin/env python3
"""
MCP Server Tool Test Script

Test script for MCP server tools functionality.
Saves test results to JSON file for verification.
"""

import json
import subprocess
import sys
import os
from datetime import datetime


def run_command(command, description):
    """Run command and capture output."""
    print(f"Running: {description}")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
        return {
            'success': result.returncode == 0,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'returncode': result.returncode
        }
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'error': 'Command timed out after 30 seconds',
            'returncode': -1
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'returncode': -2
        }


def test_mcp_tools():
    """Test MCP server tool functionality."""
    print("Testing MCP Server Tools...")
    
    test_results = {
        'timestamp': datetime.now().isoformat(),
        'tests': []
    }
    
    # Test 1: Check MCP server availability
    print("/n1. Testing MCP server availability...")
    server_test = run_command(
        "curl -f http://localhost:8080/health",
        "MCP server health check"
    )
    
    test_results['tests'].append({
        'name': 'MCP Server Health Check',
        'command': 'curl -f http://localhost:8080/health',
        'result': server_test
    })
    
    # Test 2: Test file upload functionality
    print("/n2. Testing file upload functionality...")
    # Create a simple test Excel file first
    test_file_content = '''<?xml version="1.0" encoding="UTF-8"?>
<worksheet name="Test">
<row>
    <cell><v>Test Data</v></cell>
    <cell><v>123</v></cell>
</row>
</worksheet>
</spreadsheet>'''
    
    with open('test.xlsx', 'w', encoding='utf-8') as f:
        f.write(test_file_content)
    
    upload_test = run_command(
        'curl -X POST -F "file=@test.xlsx" http://localhost:8080/upload',
        'File upload test'
    )
    
    test_results['tests'].append({
        'name': 'File Upload Test',
        'command': 'curl -X POST -F "file=@test.xlsx" http://localhost:8080/upload',
        'result': upload_test
    })
    
    # Test 3: Test GitHub integration endpoint
    print("/n3. Testing GitHub integration...")
    github_test = run_command(
        'curl -X POST -H "Content-Type: application/json" -d \'{"repo":"test","files":["test.md"]}\' http://localhost:8080/api/github/update',
        'GitHub integration test'
    )
    
    test_results['tests'].append({
        'name': 'GitHub Integration Test',
        'command': 'curl -X POST -H "Content-Type: application/json" -d \'{"repo":"test","files":["test.md"]}\' http://localhost:8080/api/github/update',
        'result': github_test
    })
    
    # Test 4: Test dashboard generation
    print("/n4. Testing dashboard generation...")
    dashboard_test = run_command(
        'curl -X GET http://localhost:8080/dashboard/test_dashboard.html',
        'Dashboard access test'
    )
    
    test_results['tests'].append({
        'name': 'Dashboard Access Test',
        'command': 'curl -X GET http://localhost:8080/dashboard/test_dashboard.html',
        'result': dashboard_test
    })
    
    # Test 5: Test Excel processing (if sample file exists)
    print("/n5. Testing Excel processing...")
    excel_test = run_command(
        'python -c "import sys; sys.path.insert(0, \'src/\'); from excel_workflow import ExcelWorkflowEngine; engine = ExcelWorkflowEngine(); print(\'Excel engine test:\', engine.test_functionality())"',
        'Excel processing engine test'
    )
    
    test_results['tests'].append({
        'name': 'Excel Processing Test',
        'command': 'python -c "import sys; sys.path.insert(0, \'src/\'); from excel_workflow import ExcelWorkflowEngine; engine = ExcelWorkflowEngine(); print(\'Excel engine test:\', engine.test_functionability())"',
        'result': excel_test
    })
    
    # Clean up test file
    if os.path.exists('test.xlsx'):
        os.remove('test.xlsx')
    
    # Save test results
    results_file = 'mcp_test_results.json'
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(test_results, f, indent=2, ensure_ascii=False)
    
    print(f"/nTest results saved to: {results_file}")
    
    # Summary
    print("/n" + "="*50)
    print("TEST SUMMARY")
    print("="*50)
    
    for i, test in enumerate(test_results['tests'], 1):
        status = "PASS" if test['result']['success'] else "FAIL"
        print(f"{i}. {test['name']}: {status}")
        if not test['result']['success']:
            print(f"   Error: {test['result'].get('error', 'Unknown error')}")
    
    print(f"/nNext steps:")
    print("- Start MCP server: python src/main.py")
    print("- Run tests: python test_mcp_tools.py")
    print("- Check results: cat mcp_test_results.json")


if __name__ == '__main__':
    test_mcp_tools()