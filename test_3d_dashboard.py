#!/usr/bin/env python3
"""
3D Dashboard Test Suite
Tests 3D functionality across different browsers and devices
"""

import os
import sys
import time
import json
import requests
import subprocess
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.firefox.options import Options as FirefoxOptions

class Dashboard3DTest:
    def __init__(self):
        self.base_url = "http://localhost:8080"
        self.test_results = {
            "timestamp": datetime.now().isoformat(),
            "browser_tests": {},
            "feature_tests": {},
            "performance_tests": {},
            "summary": {
                "total_tests": 0,
                "passed": 0,
                "failed": 0,
                "errors": []
            }
        }
        
    def start_server(self):
        """Start the Flask server"""
        try:
            print("Starting Flask server...")
            self.server_process = subprocess.Popen([
                sys.executable, "app.py"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Wait for server to start
            time.sleep(5)
            
            # Check if server is running
            response = requests.get(f"{self.base_url}/health", timeout=10)
            if response.status_code == 200:
                print("Server started successfully")
                return True
            else:
                print("❌ Server failed to start")
                return False
                
        except Exception as e:
            print(f"Error starting server: {e}")
            return False
    
    def stop_server(self):
        """Stop the Flask server"""
        if hasattr(self, 'server_process'):
            self.server_process.terminate()
            self.server_process.wait()
            print("✅ Server stopped")
    
    def test_chrome(self):
        """Test 3D dashboard in Chrome"""
        print("\n🌐 Testing Chrome browser...")
        
        try:
            options = Options()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            
            driver = webdriver.Chrome(options=options)
            results = self.run_browser_tests(driver, "Chrome")
            
            driver.quit()
            return results
            
        except Exception as e:
            print(f"❌ Chrome test failed: {e}")
            return {"status": "failed", "error": str(e)}
    
    def test_firefox(self):
        """Test 3D dashboard in Firefox"""
        print("\n🦊 Testing Firefox browser...")
        
        try:
            options = FirefoxOptions()
            options.add_argument('--headless')
            
            driver = webdriver.Firefox(options=options)
            results = self.run_browser_tests(driver, "Firefox")
            
            driver.quit()
            return results
            
        except Exception as e:
            print(f"❌ Firefox test failed: {e}")
            return {"status": "failed", "error": str(e)}
    
    def run_browser_tests(self, driver, browser_name):
        """Run comprehensive tests in a browser"""
        results = {
            "browser": browser_name,
            "tests": {},
            "performance": {},
            "features": {}
        }
        
        try:
            # Navigate to 3D dashboard
            driver.get(f"{self.base_url}/dashboard-3d")
            wait = WebDriverWait(driver, 10)
            
            # Test 1: Page Load
            print(f"  📄 Testing page load...")
            try:
                wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                results["tests"]["page_load"] = {"status": "passed", "time": time.time()}
                print("    ✅ Page loaded successfully")
            except Exception as e:
                results["tests"]["page_load"] = {"status": "failed", "error": str(e)}
                print(f"    ❌ Page load failed: {e}")
            
            # Test 2: 3D Background
            print(f"  🎨 Testing 3D background...")
            try:
                background = driver.find_element(By.CLASS_NAME, "background-3d")
                results["tests"]["3d_background"] = {"status": "passed"}
                print("    ✅ 3D background found")
            except Exception as e:
                results["tests"]["3d_background"] = {"status": "failed", "error": str(e)}
                print(f"    ❌ 3D background not found: {e}")
            
            # Test 3: 3D Navigation
            print(f"  🧭 Testing 3D navigation...")
            try:
                nav = driver.find_element(By.CLASS_NAME, "nav-3d")
                results["tests"]["3d_navigation"] = {"status": "passed"}
                print("    ✅ 3D navigation found")
            except Exception as e:
                results["tests"]["3d_navigation"] = {"status": "failed", "error": str(e)}
                print(f"    ❌ 3D navigation not found: {e}")
            
            # Test 4: 3D Upload Area
            print(f"  📤 Testing 3D upload area...")
            try:
                upload = driver.find_element(By.CLASS_NAME, "upload-3d-container")
                results["tests"]["3d_upload"] = {"status": "passed"}
                print("    ✅ 3D upload area found")
            except Exception as e:
                results["tests"]["3d_upload"] = {"status": "failed", "error": str(e)}
                print(f"    ❌ 3D upload area not found: {e}")
            
            # Test 5: JavaScript Functionality
            print(f"  ⚡ Testing JavaScript functionality...")
            try:
                # Check if 3D framework is loaded
                js_result = driver.execute_script("return typeof window.framework3D !== 'undefined'")
                results["tests"]["js_framework"] = {"status": "passed" if js_result else "failed"}
                print(f"    {'✅' if js_result else '❌'} 3D framework loaded")
                
                # Check if background is initialized
                bg_result = driver.execute_script("return typeof window.background3D !== 'undefined'")
                results["tests"]["js_background"] = {"status": "passed" if bg_result else "failed"}
                print(f"    {'✅' if bg_result else '❌'} 3D background initialized")
                
                # Check if notifications work
                notif_result = driver.execute_script("return typeof window.notify3D !== 'undefined'")
                results["tests"]["js_notifications"] = {"status": "passed" if notif_result else "failed"}
                print(f"    {'✅' if notif_result else '❌'} 3D notifications available")
                
            except Exception as e:
                results["tests"]["javascript"] = {"status": "failed", "error": str(e)}
                print(f"    ❌ JavaScript test failed: {e}")
            
            # Test 6: Performance Metrics
            print(f"  📊 Testing performance...")
            try:
                # Get page load time
                load_time = driver.execute_script("return performance.timing.loadEventEnd - performance.timing.navigationStart")
                results["performance"]["page_load_time"] = load_time
                print(f"    ⏱️ Page load time: {load_time}ms")
                
                # Check for 3D transforms
                transforms = driver.execute_script("""
                    var elements = document.querySelectorAll('[style*="transform3d"], [style*="translateZ"]');
                    return elements.length;
                """)
                results["performance"]["3d_elements"] = transforms
                print(f"    🎭 3D elements found: {transforms}")
                
            except Exception as e:
                results["performance"]["error"] = str(e)
                print(f"    ❌ Performance test failed: {e}")
            
            # Test 7: Responsive Design
            print(f"  📱 Testing responsive design...")
            try:
                # Test mobile view
                driver.set_window_size(375, 667)
                time.sleep(2)
                
                mobile_nav = driver.find_element(By.CLASS_NAME, "nav-3d-mobile-toggle")
                results["tests"]["responsive_mobile"] = {"status": "passed"}
                print("    ✅ Mobile navigation works")
                
                # Test desktop view
                driver.set_window_size(1920, 1080)
                time.sleep(2)
                
                desktop_nav = driver.find_element(By.CLASS_NAME, "nav-3d-menu")
                results["tests"]["responsive_desktop"] = {"status": "passed"}
                print("    ✅ Desktop navigation works")
                
            except Exception as e:
                results["tests"]["responsive"] = {"status": "failed", "error": str(e)}
                print(f"    ❌ Responsive test failed: {e}")
            
            results["status"] = "completed"
            return results
            
        except Exception as e:
            results["status"] = "failed"
            results["error"] = str(e)
            print(f"❌ Browser test failed: {e}")
            return results
    
    def test_api_endpoints(self):
        """Test API endpoints"""
        print("\n🔌 Testing API endpoints...")
        
        endpoints = [
            "/health",
            "/api/stats",
            "/api/processed-data",
            "/api/excel-files"
        ]
        
        results = {}
        
        for endpoint in endpoints:
            try:
                response = requests.get(f"{self.base_url}{endpoint}", timeout=10)
                results[endpoint] = {
                    "status_code": response.status_code,
                    "response_time": response.elapsed.total_seconds(),
                    "success": response.status_code == 200
                }
                print(f"  ✅ {endpoint}: {response.status_code}")
                
            except Exception as e:
                results[endpoint] = {
                    "status": "failed",
                    "error": str(e)
                }
                print(f"  ❌ {endpoint}: {e}")
        
        return results
    
    def test_3d_features(self):
        """Test specific 3D features"""
        print("\n🎮 Testing 3D features...")
        
        features = {}
        
        # Test WebGL support
        try:
            options = Options()
            options.add_argument('--headless')
            driver = webdriver.Chrome(options=options)
            driver.get(f"{self.base_url}/dashboard-3d")
            
            webgl_support = driver.execute_script("""
                var canvas = document.createElement('canvas');
                var gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
                return gl && gl.getExtension('OES_texture_float');
            """)
            
            features["webgl_support"] = webgl_support
            print(f"  {'✅' if webgl_support else '❌'} WebGL support: {webgl_support}")
            
            # Test CSS 3D transforms
            css3d_support = driver.execute_script("""
                var div = document.createElement('div');
                div.style.transform = 'translateZ(0)';
                return div.style.transform !== '';
            """)
            
            features["css3d_support"] = css3d_support
            print(f"  {'✅' if css3d_support else '❌'} CSS 3D transforms: {css3d_support}")
            
            # Test Three.js loading
            threejs_loaded = driver.execute_script("return typeof THREE !== 'undefined'")
            features["threejs_loaded"] = threejs_loaded
            print(f"  {'✅' if threejs_loaded else '❌'} Three.js loaded: {threejs_loaded}")
            
            driver.quit()
            
        except Exception as e:
            features["error"] = str(e)
            print(f"  ❌ 3D feature test failed: {e}")
        
        return features
    
    def generate_report(self):
        """Generate comprehensive test report"""
        print("\n📋 Generating test report...")
        
        # Calculate summary
        total_tests = 0
        passed_tests = 0
        
        for browser_name, results in self.test_results["browser_tests"].items():
            if isinstance(results.get("tests"), dict):
                for test_name, test_result in results["tests"].items():
                    total_tests += 1
                    if test_result.get("status") == "passed":
                        passed_tests += 1
        
        self.test_results["summary"]["total_tests"] = total_tests
        self.test_results["summary"]["passed"] = passed_tests
        self.test_results["summary"]["failed"] = total_tests - passed_tests
        
        # Save report
        report_file = f"3d_dashboard_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(report_file, 'w') as f:
            json.dump(self.test_results, f, indent=2)
        
        print(f"📄 Report saved to: {report_file}")
        
        # Print summary
        print(f"\n📊 Test Summary:")
        print(f"  Total Tests: {total_tests}")
        print(f"  Passed: {passed_tests}")
        print(f"  Failed: {total_tests - passed_tests}")
        print(f"  Success Rate: {(passed_tests/total_tests*100):.1f}%" if total_tests > 0 else "N/A")
        
        return report_file
    
    def run_all_tests(self):
        """Run all tests"""
        print("Starting 3D Dashboard Test Suite")
        print("=" * 50)
        
        # Start server
        if not self.start_server():
            return False
        
        try:
            # Test API endpoints
            self.test_results["api_tests"] = self.test_api_endpoints()
            
            # Test 3D features
            self.test_results["feature_tests"] = self.test_3d_features()
            
            # Test browsers
            self.test_results["browser_tests"]["Chrome"] = self.test_chrome()
            self.test_results["browser_tests"]["Firefox"] = self.test_firefox()
            
            # Generate report
            report_file = self.generate_report()
            
            return report_file
            
        finally:
            # Stop server
            self.stop_server()

if __name__ == "__main__":
    tester = Dashboard3DTest()
    report = tester.run_all_tests()
    
    if report:
        print(f"\n✅ Testing completed! Report: {report}")
    else:
        print("\n❌ Testing failed!")
        sys.exit(1)