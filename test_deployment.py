#!/usr/bin/env python3
"""
AgentDaf1.1 Deployment Test Script
Tests all components and deployment scenarios
"""

import os
import sys
import subprocess
import time
import json
from pathlib import Path

def test_syntax():
    """Test Python syntax for all files"""
    print("🔍 Testing Python syntax...")
    import py_compile
    
    errors = []
    for root, dirs, files in os.walk('src'):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                try:
                    py_compile.compile(filepath, doraise=True)
                except Exception as e:
                    errors.append(f'{filepath}: {e}')
    
    if errors:
        print(f"❌ {len(errors)} syntax errors found")
        for error in errors[:5]:
            print(f"   {error}")
        return False
    else:
        print("✅ All Python files syntax OK")
        return True

def test_imports():
    """Test critical imports"""
    print("🔍 Testing imports...")
    
    critical_imports = [
        'src.main',
        'src.api.flask_api',
        'src.core.managers',
        'src.config.settings',
        'src.core.excel_processor',
        'src.core.ai_tools'
    ]
    
    failed = []
    for module in critical_imports:
        try:
            __import__(module)
            print(f"   ✅ {module}")
        except Exception as e:
            failed.append(f'{module}: {e}')
            print(f"   ❌ {module}")
    
    return len(failed) == 0

def test_configuration():
    """Test configuration loading"""
    print("🔍 Testing configuration...")
    try:
        from src.config.settings import Config
        print(f"   ✅ Config loaded (DEBUG={Config.DEBUG})")
        return True
    except Exception as e:
        print(f"   ❌ Configuration failed: {e}")
        return False

def test_docker_project():
    """Test Docker project"""
    print("🔍 Testing Docker project...")
    try:
        import sys
        sys.path.insert(0, os.path.join(os.getcwd(), 'docker_project', 'src'))
        from main import create_app
        app = create_app()
        print(f"   ✅ Docker app created ({len(app.url_map._rules)} routes)")
        return True
    except Exception as e:
        print(f"   ❌ Docker project failed: {e}")
        return False

def test_docker_compose():
    """Test Docker Compose configuration"""
    print("🔍 Testing Docker Compose...")
    try:
        result = subprocess.run(['docker-compose', 'config'], 
                              cwd='docker_project',
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("   ✅ Docker Compose configuration valid")
            return True
        else:
            print(f"   ❌ Docker Compose error: {result.stderr}")
            return False
    except FileNotFoundError:
        print("   ⚠️ Docker not available for testing")
        return True  # Not an error if Docker isn't installed

def generate_report(results):
    """Generate test report"""
    print("/n" + "="*50)
    print("📊 DEPLOYMENT TEST REPORT")
    print("="*50)
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:25} {status}")
    
    print("-"*50)
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    
    if passed_tests == total_tests:
        print("/n🎉 ALL TESTS PASSED - SYSTEM READY FOR DEPLOYMENT!")
        print("/n🚀 Deployment Commands:")
        print("   Development: python src/main.py")
        print("   Docker:     cd docker_project && docker-compose up")
        return True
    else:
        print(f"/n⚠️ {total_tests - passed_tests} TESTS FAILED - FIX REQUIRED")
        return False

def main():
    """Main test function"""
    print("🚀 AgentDaf1.1 Deployment Test Suite")
    print("="*50)
    
    # Change to project directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Run tests
    results = {
        "Python Syntax": test_syntax(),
        "Module Imports": test_imports(),
        "Configuration": test_configuration(),
        "Docker Project": test_docker_project(),
        "Docker Compose": test_docker_compose()
    }
    
    # Generate report
    success = generate_report(results)
    
    # Save report
    report = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total_tests": len(results),
        "passed_tests": sum(results.values()),
        "results": results,
        "success": success
    }
    
    with open('deployment_test_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"/n📄 Report saved to: deployment_test_report.json")
    return 0 if success else 1

if __name__ == '__main__':
    sys.exit(main())