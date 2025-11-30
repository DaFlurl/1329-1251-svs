"""
Test Framework for AgentDaf1.1
Comprehensive testing suite for all components
"""

import unittest
import tempfile
import os
import json
import sys
from pathlib import Path
import logging

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.excel_processor import ExcelProcessor
from src.core.dashboard_generator import DashboardGenerator
from src.api.github_integration import GitHubIntegration
from src.config.settings import Config

logger = logging.getLogger(__name__)

class TestExcelProcessor(unittest.TestCase):
    """Test cases for Excel processing"""
    
    def setUp(self):
        """Setup test environment"""
        self.processor = ExcelProcessor()
        self.test_data_dir = os.path.join(os.path.dirname(__file__), 'test_data')
        os.makedirs(self.test_data_dir, exist_ok=True)
    
    def test_validate_data_valid(self):
        """Test data validation with valid data"""
        valid_data = {
            'sheets': {
                'Sheet1': {
                    'name': 'Sheet1',
                    'rows': 10,
                    'columns': 5,
                    'data': [{'col1': 'value1'}],
                    'headers': ['col1', 'col2'],
                    'statistics': {'numeric_columns': [], 'text_columns': []}
                }
            }
        }
        
        result = self.processor.validate_data(valid_data)
        self.assertTrue(result['is_valid'])
        self.assertEqual(len(result['errors']), 0)
    
    def test_validate_data_empty(self):
        """Test data validation with empty data"""
        empty_data = {'sheets': {}}
        
        result = self.processor.validate_data(empty_data)
        self.assertFalse(result['is_valid'])
        self.assertIn('No sheets found', result['errors'])
    
    def test_process_game_data(self):
        """Test game data processing"""
        test_data = {
            'sheets': {
                'Game1': {
                    'name': 'Game1',
                    'rows': 5,
                    'columns': 3,
                    'data': [
                        {'player': 'Alice', 'score': 100},
                        {'player': 'Bob', 'score': 150}
                    ],
                    'headers': ['player', 'score'],
                    'statistics': {
                        'numeric_columns': [{'name': 'score', 'mean': 125}],
                        'text_columns': [{'name': 'player', 'unique_values': 2}]
                    }
                }
            }
        }
        
        result = self.processor.process_game_data(test_data)
        
        self.assertIn('summary', result)
        self.assertIn('games', result)
        self.assertIn('charts', result)
        self.assertEqual(result['summary']['total_games'], 1)
        self.assertEqual(result['summary']['total_players'], 5)

class TestDashboardGenerator(unittest.TestCase):
    """Test cases for dashboard generation"""
    
    def setUp(self):
        """Setup test environment"""
        self.generator = DashboardGenerator()
        self.test_output_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Cleanup test environment"""
        import shutil
        shutil.rmtree(self.test_output_dir, ignore_errors=True)
    
    def test_create_dashboard(self):
        """Test dashboard creation"""
        test_data = {
            'summary': {
                'total_games': 2,
                'total_players': 20
            },
            'games': [
                {
                    'sheet_name': 'Game1',
                    'total_players': 10,
                    'stats': {'numeric_columns': [], 'text_columns': []}
                }
            ]
        }
        
        html = self.generator.create_dashboard(test_data, "Test Dashboard")
        
        self.assertIsInstance(html, str)
        self.assertIn('Test Dashboard', html)
        self.assertIn('Gesamtspiele', html)
        self.assertIn('2', html)
    
    def test_save_dashboard(self):
        """Test dashboard saving"""
        test_html = "<html><body>Test</body></html>"
        test_file = os.path.join(self.test_output_dir, 'test_dashboard.html')
        
        result = self.generator.save_dashboard(test_html, test_file)
        
        self.assertTrue(result)
        self.assertTrue(os.path.exists(test_file))
        
        with open(test_file, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertEqual(content, test_html)

class TestGitHubIntegration(unittest.TestCase):
    """Test cases for GitHub integration"""
    
    def setUp(self):
        """Setup test environment"""
        self.config = {
            'GITHUB_TOKEN': 'test_token',
            'GITHUB_REPO_OWNER': 'test_owner',
            'GITHUB_REPO_NAME': 'test_repo'
        }
        self.github = GitHubIntegration(self.config)
    
    def test_is_configured(self):
        """Test configuration check"""
        self.assertTrue(self.github._is_configured())
        
        # Test missing configuration
        incomplete_config = {'GITHUB_TOKEN': 'test_token'}
        incomplete_github = GitHubIntegration(incomplete_config)
        self.assertFalse(incomplete_github._is_configured())
    
    def test_update_files_not_configured(self):
        """Test file update without configuration"""
        incomplete_config = {'GITHUB_TOKEN': 'test_token'}
        incomplete_github = GitHubIntegration(incomplete_config)
        
        result = incomplete_github.update_files({'dashboards': []})
        self.assertFalse(result['success'])
        self.assertIn('not configured', result['error'])

class TestConfig(unittest.TestCase):
    """Test cases for configuration"""
    
    def test_config_values(self):
        """Test configuration values"""
        self.assertIsInstance(Config.SECRET_KEY, str)
        self.assertGreater(len(Config.SECRET_KEY), 10)
        self.assertIsInstance(Config.ALLOWED_EXTENSIONS, list)
        self.assertIn('xlsx', Config.ALLOWED_EXTENSIONS)
        self.assertIn('xls', Config.ALLOWED_EXTENSIONS)

class TestAPIEndpoints(unittest.TestCase):
    """Test API endpoints"""
    
    def setUp(self):
        """Setup test environment"""
        from src.api.flask_api import FlaskAPI
        self.app = FlaskAPI()
        self.client = self.app.app.test_client()
        self.app.app.config['TESTING'] = True
    
    def test_health_endpoint(self):
        """Test health check endpoint"""
        response = self.client.get('/api/health')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'healthy')
        self.assertIn('timestamp', data)
    
    def test_upload_no_file(self):
        """Test upload endpoint without file"""
        response = self.client.post('/api/upload')
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_stats_endpoint(self):
        """Test statistics endpoint"""
        response = self.client.get('/api/stats')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('system', data)
        self.assertIn('dashboards', data)
        self.assertIn('processor', data)

class TestIntegration(unittest.TestCase):
    """Integration tests"""
    
    def test_full_workflow(self):
        """Test complete workflow from upload to dashboard"""
        # This would require actual Excel files for full testing
        # For now, test component integration
        processor = ExcelProcessor()
        generator = DashboardGenerator()
        
        # Test that components work together
        test_data = {
            'sheets': {
                'Test': {
                    'name': 'Test',
                    'rows': 1,
                    'columns': 1,
                    'data': [{'test': 'value'}],
                    'headers': ['test'],
                    'statistics': {'numeric_columns': [], 'text_columns': []}
                }
            }
        }
        
        # Process data
        validation = processor.validate_data(test_data)
        self.assertTrue(validation['is_valid'])
        
        processed = processor.process_game_data(test_data)
        self.assertIn('summary', processed)
        
        # Generate dashboard
        html = generator.create_dashboard(processed, "Integration Test")
        self.assertIsInstance(html, str)
        self.assertIn('Integration Test', html)

def create_test_excel_file():
    """Create a test Excel file for testing"""
    try:
        import pandas as pd
        
        # Create test data
        test_data = {
            'Spieler': ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve'],
            'Punkte': [100, 150, 200, 175, 125],
            'Datum': ['2024-01-01', '2024-01-02', '2024-01-03', '2024-01-04', '2024-01-05']
        }
        
        df = pd.DataFrame(test_data)
        test_file = os.path.join(os.path.dirname(__file__), 'test_data', 'test_game_data.xlsx')
        
        os.makedirs(os.path.dirname(test_file), exist_ok=True)
        df.to_excel(test_file, index=False)
        
        return test_file
        
    except Exception as e:
        logger.error(f"Error creating test Excel file: {str(e)}")
        return None

def run_performance_tests():
    """Run performance tests"""
    print("Running performance tests...")
    
    # Test Excel processing performance
    processor = ExcelProcessor()
    test_file = create_test_excel_file()
    
    if test_file and os.path.exists(test_file):
        import time
        start_time = time.time()
        
        data = processor.read_excel_file(test_file)
        validation = processor.validate_data(data)
        processed = processor.process_game_data(data)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        print(f"Excel processing performance: {processing_time:.2f} seconds")
        print(f"Data points processed: {len(processed.get('games', []))}")
        print(f"Validation passed: {validation['is_valid']}")
        
        # Cleanup
        os.remove(test_file)

if __name__ == '__main__':
    # Setup logging for tests
    logging.basicConfig(level=logging.INFO)
    
    print("""
╔══════════════════════════════════════════════════════════╗
║                AgentDaf1.1 Test Suite                      ║
║                                                              ║
║  🧪 Running Unit Tests...                                   ║
║  🔍 Testing Components...                                      ║
║  📊 Performance Tests...                                      ║
╚════════════════════════════════════════════════════════════╝
    """)
    
    # Run unit tests
    unittest.main(argv=[''], exit=False, verbosity=2)
    
    # Run performance tests
    run_performance_tests()
    
    print("/n✅ All tests completed!")