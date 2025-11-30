#!/usr/bin/env python3
"""
AgentDaf1.1 Production Test Suite
Comprehensive testing for production deployment
"""

import unittest
import json
import time
import requests
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

class TestAgentDafProduction(unittest.TestCase):
    """Production Test Suite for AgentDaf1.1"""
    
    BASE_URL = "http://localhost:8080"
    
    @classmethod
    def setUpClass(cls):
        """Setup test environment"""
        cls.session = requests.Session()
        cls.session.timeout = 10
        
    def test_01_health_check(self):
        """Test health check endpoint"""
        response = self.session.get(f"{self.BASE_URL}/api/health")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(data['status'], 'healthy')
        self.assertIn('system', data)
        self.assertIn('version', data)
        
    def test_02_main_dashboard(self):
        """Test main dashboard loads"""
        response = self.session.get(self.BASE_URL)
        self.assertEqual(response.status_code, 200)
        self.assertIn('AgentDaf1.1', response.text)
        self.assertIn('Dashboard', response.text)
        
    def test_03_players_api(self):
        """Test players API endpoint"""
        response = self.session.get(f"{self.BASE_URL}/api/players")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertIn('data', data)
        self.assertIsInstance(data['data'], list)
        self.assertGreater(len(data['data']), 0)
        
        # Test player data structure
        player = data['data'][0]
        self.assertIn('name', player)
        self.assertIn('score', player)
        self.assertIn('alliance', player)
        
    def test_04_alliances_api(self):
        """Test alliances API endpoint"""
        response = self.session.get(f"{self.BASE_URL}/api/alliances")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertIn('data', data)
        self.assertIsInstance(data['data'], list)
        self.assertGreater(len(data['data']), 0)
        
        # Test alliance data structure
        alliance = data['data'][0]
        self.assertIn('name', alliance)
        self.assertIn('total_score', alliance)
        self.assertIn('members', alliance)
        
    def test_05_complete_data_api(self):
        """Test complete data API endpoint"""
        response = self.session.get(f"{self.BASE_URL}/api/data")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertIn('data', data)
        
        complete_data = data['data']
        self.assertIn('players', complete_data)
        self.assertIn('alliances', complete_data)
        
    def test_06_metrics_endpoint(self):
        """Test metrics endpoint"""
        response = self.session.get(f"{self.BASE_URL}/api/metrics")
        self.assertEqual(response.status_code, 200)
        self.assertIn('agentdaf_requests_total', response.text)
        
    def test_07_cors_headers(self):
        """Test CORS headers are present"""
        response = self.session.options(f"{self.BASE_URL}/api/health")
        self.assertIn('Access-Control-Allow-Origin', response.headers)
        
    def test_08_response_time(self):
        """Test API response times"""
        start_time = time.time()
        response = self.session.get(f"{self.BASE_URL}/api/health")
        end_time = time.time()
        
        response_time = end_time - start_time
        self.assertLess(response_time, 2.0, "Health check response too slow")
        self.assertEqual(response.status_code, 200)
        
    def test_09_error_handling(self):
        """Test error handling for invalid endpoints"""
        response = self.session.get(f"{self.BASE_URL}/api/nonexistent")
        self.assertEqual(response.status_code, 404)
        
    def test_10_data_consistency(self):
        """Test data consistency across endpoints"""
        # Get players from players endpoint
        players_response = self.session.get(f"{self.BASE_URL}/api/players")
        players_data = players_response.json()['data']
        
        # Get complete data
        complete_response = self.session.get(f"{self.BASE_URL}/api/data")
        complete_data = complete_response.json()['data']['players']
        
        # Compare data
        self.assertEqual(len(players_data), len(complete_data))
        self.assertEqual(players_data[0]['name'], complete_data[0]['name'])

class TestPerformance(unittest.TestCase):
    """Performance and load testing"""
    
    BASE_URL = "http://localhost:8080"
    
    def test_concurrent_requests(self):
        """Test handling concurrent requests"""
        import threading
        import queue
        
        results = queue.Queue()
        
        def make_request():
            try:
                response = requests.get(f"{self.BASE_URL}/api/health", timeout=5)
                results.put(response.status_code)
            except Exception as e:
                results.put(str(e))
        
        # Start 10 concurrent requests
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Check results
        success_count = 0
        while not results.empty():
            result = results.get()
            if result == 200:
                success_count += 1
        
        self.assertGreaterEqual(success_count, 8, "Too many failed concurrent requests")

class TestSecurity(unittest.TestCase):
    """Security testing"""
    
    BASE_URL = "http://localhost:8080"
    
    def test_security_headers(self):
        """Test security headers are present"""
        response = requests.get(self.BASE_URL)
        
        # Check for common security headers
        headers_to_check = [
            'X-Content-Type-Options',
            'X-Frame-Options',
            'X-XSS-Protection'
        ]
        
        for header in headers_to_check:
            self.assertIn(header, response.headers, f"Missing security header: {header}")

def run_production_tests():
    """Run all production tests"""
    print("🧪 Starting AgentDaf1.1 Production Test Suite")
    print("=" * 50)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestAgentDafProduction))
    suite.addTests(loader.loadTestsFromTestCase(TestPerformance))
    suite.addTests(loader.loadTestsFromTestCase(TestSecurity))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("/n" + "=" * 50)
    print("📊 Test Results Summary:")
    print(f"Tests Run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success Rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print("/n❌ Failures:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback.split('AssertionError:')[-1].strip()}")
    
    if result.errors:
        print("/n💥 Errors:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback.split('Exception:')[-1].strip()}")
    
    if result.wasSuccessful():
        print("/n✅ All tests passed! System is production ready.")
        return True
    else:
        print("/n⚠️  Some tests failed. Review issues before production deployment.")
        return False

if __name__ == "__main__":
    success = run_production_tests()
    sys.exit(0 if success else 1)