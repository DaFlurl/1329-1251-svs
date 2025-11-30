# -*- coding: utf-8 -*-
"""
Comprehensive Testing Strategy for Memory System and AI Tools
Advanced testing framework with unit tests, integration tests, and performance benchmarks
"""

import unittest
import tempfile
import shutil
import json
import time
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import sys
import os

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from src.tools.neural_memory import MemoryManager, NeuralMemorySystem
    from src.tools.ai_tools import AIToolsSuite, CodeIntelligenceAnalyzer, AutomatedTestGenerator, PerformanceProfiler
except ImportError as e:
    print(f"Import error: {e}")
    # Continue with test even if imports fail
    MemoryManager = None
    NeuralMemorySystem = None
    AIToolsSuite = None
    CodeIntelligenceAnalyzer = None
    AutomatedTestGenerator = None
    PerformanceProfiler = None

class TestNeuralMemorySystem(unittest.TestCase):
    """Test suite for Neural Memory System"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.memory_manager = MemoryManager(self.test_dir)
    
    def tearDown(self):
        """Clean up test environment"""
        self.memory_manager.shutdown()
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_working_memory_storage(self):
        """Test working memory storage and retrieval"""
        content = "Test working memory item"
        memory_id = self.memory_manager.remember(
            content, 
            "working", 
            importance=0.8, 
            tags=["test", "working"]
        )
        
        self.assertIsNotNone(memory_id)
        
        # Test retrieval
        results = self.memory_manager.recall("Test", "working")
        self.assertGreater(len(results), 0)
        self.assertEqual(results[0].content, content)
    
    def test_episodic_memory_storage(self):
        """Test episodic memory storage and retrieval"""
        content = "Test episodic memory item"
        context = {"action": "test", "location": "unittest"}
        
        memory_id = self.memory_manager.remember(
            content,
            "episodic",
            context=context,
            importance=0.7,
            tags=["test", "episodic"]
        )
        
        self.assertIsNotNone(memory_id)
        
        # Test retrieval
        results = self.memory_manager.recall("Test", "episodic")
        self.assertGreater(len(results), 0)
        self.assertEqual(results[0].content, content)
    
    def test_semantic_memory_storage(self):
        """Test semantic memory storage and retrieval"""
        content = "Python is a programming language"
        category = "programming"
        
        memory_id = self.memory_manager.remember(
            content,
            "semantic",
            category=category,
            relationships=["language", "technology"],
            importance=0.9,
            tags=["python", "programming"]
        )
        
        self.assertIsNotNone(memory_id)
        
        # Test retrieval
        results = self.memory_manager.recall("Python", "semantic")
        self.assertGreater(len(results), 0)
        self.assertEqual(results[0].content, content)
    
    def test_memory_statistics(self):
        """Test memory statistics functionality"""
        # Add some memories
        self.memory_manager.remember("Test 1", "working")
        self.memory_manager.remember("Test 2", "episodic")
        self.memory_manager.remember("Test 3", "semantic")
        
        stats = self.memory_manager.get_stats()
        
        self.assertIn('working_memory_count', stats)
        self.assertIn('episodic_memory_count', stats)
        self.assertIn('semantic_memory_count', stats)
        self.assertIn('total_memories', stats)
    
    def test_memory_export(self):
        """Test memory export functionality"""
        # Add some memories
        self.memory_manager.remember("Export test", "working")
        
        export_file = Path(self.test_dir) / "test_export.json"
        self.memory_manager.export(str(export_file))
        
        self.assertTrue(export_file.exists())
        
        # Verify export content
        with open(export_file, 'r', encoding='utf-8') as f:
            export_data = json.load(f)
        
        self.assertIn('export_timestamp', export_data)
        self.assertIn('working_memory', export_data)
        self.assertIn('episodic_memory', export_data)
        self.assertIn('semantic_memory', export_data)

class TestAIToolsSuite(unittest.TestCase):
    """Test suite for AI Tools"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.ai_tools = AIToolsSuite()
        
        # Create a test Python file
        self.test_file = Path(self.test_dir) / "test_code.py"
        self.test_file.write_text("""
def test_function(x, y):
    /"/"/"Test function for analysis/"/"/"
    if x > 0:
        return x + y
    else:
        return x - y

class TestClass:
    def __init__(self):
        self.value = 42
    
    def method(self):
        return self.value * 2
""")
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_code_analysis(self):
        """Test code analysis functionality"""
        analysis = self.ai_tools.code_analyzer.analyze_file(str(self.test_file))
        
        self.assertIsNotNone(analysis)
        self.assertGreater(analysis.complexity_score, 0)
        self.assertIn('lines_of_code', analysis.metrics)
        self.assertIn('functions', analysis.metrics)
        self.assertIn('classes', analysis.metrics)
    
    def test_test_generation(self):
        """Test automated test generation"""
        test_content = self.ai_tools.test_generator.generate_tests_for_file(str(self.test_file))
        
        self.assertIn('def test_test_function', test_content)
        self.assertIn('def test_TestClass_integration', test_content)
        self.assertIn('Auto-generated tests', test_content)
    
    def test_performance_profiling(self):
        """Test performance profiling"""
        def test_function():
            time.sleep(0.1)
            return sum(range(1000))
        
        profile = self.ai_tools.profiler.profile_function("test_function", test_function)
        
        self.assertIsNotNone(profile)
        self.assertGreater(profile.execution_time, 0.1)
        self.assertEqual(profile.function_name, "test_function")
        self.assertEqual(profile.call_count, 1)
    
    def test_project_analysis(self):
        """Test project-wide analysis"""
        # Create additional test files
        (Path(self.test_dir) / "module1.py").write_text("def func1(): pass")
        (Path(self.test_dir) / "module2.py").write_text("class Class1: pass")
        
        analysis = self.ai_tools.analyze_project(self.test_dir)
        
        self.assertIn('project_path', analysis)
        self.assertIn('files_analyzed', analysis)
        self.assertIn('total_issues', analysis)
        self.assertIn('average_complexity', analysis)
        self.assertGreater(analysis['files_analyzed'], 0)
    
    def test_continuous_monitoring(self):
        """Test continuous performance monitoring"""
        # Start monitoring
        self.ai_tools.profiler.start_monitoring(interval=0.1)
        
        # Let it run for a short time
        time.sleep(0.3)
        
        # Stop monitoring
        self.ai_tools.profiler.stop_monitoring()
        
        # Check if profiles were collected
        summary = self.ai_tools.profiler.get_performance_summary()
        self.assertIn('system_monitor', summary)

class TestIntegration(unittest.TestCase):
    """Integration tests for memory system and AI tools"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.memory_manager = MemoryManager(self.test_dir)
        self.ai_tools = AIToolsSuite()
    
    def tearDown(self):
        """Clean up test environment"""
        self.memory_manager.shutdown()
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_memory_ai_integration(self):
        """Test integration between memory system and AI tools"""
        # Store code analysis results in memory
        test_file = Path(self.test_dir) / "integration_test.py"
        test_file.write_text("def integration_test(): return True")
        
        analysis = self.ai_tools.code_analyzer.analyze_file(str(test_file))
        
        # Store analysis in episodic memory
        self.memory_manager.remember(
            f"Code analysis completed for {test_file.name}",
            "episodic",
            context={
                "file": str(test_file),
                "complexity": analysis.complexity_score,
                "issues_count": len(analysis.issues)
            },
            importance=0.8,
            tags=["code_analysis", "integration_test"]
        )
        
        # Retrieve from memory
        results = self.memory_manager.recall("code analysis", "episodic")
        self.assertGreater(len(results), 0)
        
        # Store suggestions in semantic memory
        for suggestion in analysis.suggestions:
            self.memory_manager.remember(
                suggestion,
                "semantic",
                category="code_improvement",
                importance=0.7,
                tags=["suggestion", "code_quality"]
            )
        
        # Retrieve suggestions
        suggestions = self.memory_manager.recall("improvement", "semantic")
        self.assertGreater(len(suggestions), 0)
    
    def test_performance_memory_tracking(self):
        """Test performance tracking with memory system"""
        def performance_test():
            return sum(range(10000))
        
        # Profile function
        profile = self.ai_tools.profiler.profile_function("performance_test", performance_test)
        
        # Store performance data in memory
        self.memory_manager.remember(
            f"Performance test completed: {profile.function_name}",
            "episodic",
            context={
                "execution_time": profile.execution_time,
                "memory_usage": profile.memory_usage,
                "timestamp": profile.timestamp.isoformat()
            },
            importance=0.6,
            tags=["performance", "profiling"]
        )
        
        # Retrieve performance data
        results = self.memory_manager.recall("performance", "episodic")
        self.assertGreater(len(results), 0)

class TestPerformanceBenchmarks(unittest.TestCase):
    """Performance benchmarks for memory system and AI tools"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.memory_manager = MemoryManager(self.test_dir)
        self.ai_tools = AIToolsSuite()
    
    def tearDown(self):
        """Clean up test environment"""
        self.memory_manager.shutdown()
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_memory_performance(self):
        """Test memory system performance"""
        # Benchmark memory operations
        start_time = time.time()
        
        # Store 100 memories
        for i in range(100):
            self.memory_manager.remember(f"Memory item {i}", "working")
        
        storage_time = time.time() - start_time
        
        # Benchmark retrieval
        start_time = time.time()
        results = self.memory_manager.recall("Memory", "working")
        retrieval_time = time.time() - start_time
        
        # Performance assertions
        self.assertLess(storage_time, 5.0, "Memory storage should be fast")
        self.assertLess(retrieval_time, 1.0, "Memory retrieval should be fast")
        self.assertGreater(len(results), 50, "Should retrieve most memories")
        
        print(f"Memory storage: {storage_time:.3f}s for 100 items")
        print(f"Memory retrieval: {retrieval_time:.3f}s for {len(results)} results")
    
    def test_ai_tools_performance(self):
        """Test AI tools performance"""
        # Create test file
        test_file = Path(self.test_dir) / "performance_test.py"
        test_file.write_text("""
def complex_function(x, y, z):
    if x > 0:
        if y > 0:
            if z > 0:
                return x + y + z
            else:
                return x + y - z
        else:
            if z > 0:
                return x - y + z
            else:
                return x - y - z
    else:
        return 0
""")
        
        # Benchmark code analysis
        start_time = time.time()
        analysis = self.ai_tools.code_analyzer.analyze_file(str(test_file))
        analysis_time = time.time() - start_time
        
        # Benchmark test generation
        start_time = time.time()
        test_content = self.ai_tools.test_generator.generate_tests_for_file(str(test_file))
        generation_time = time.time() - start_time
        
        # Performance assertions
        self.assertLess(analysis_time, 2.0, "Code analysis should be fast")
        self.assertLess(generation_time, 1.0, "Test generation should be fast")
        self.assertGreater(len(test_content), 100, "Should generate substantial test content")
        
        print(f"Code analysis: {analysis_time:.3f}s")
        print(f"Test generation: {generation_time:.3f}s")

def run_comprehensive_tests():
    """Run comprehensive test suite"""
    print("🧪 Running Comprehensive Test Suite")
    print("=" * 50)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestNeuralMemorySystem))
    test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestAIToolsSuite))
    test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestIntegration))
    test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestPerformanceBenchmarks))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Generate report
    report = {
        "test_run_timestamp": datetime.now().isoformat(),
        "total_tests": result.testsRun,
        "failures": len(result.failures),
        "errors": len(result.errors),
        "success_rate": (result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100,
        "passed": result.testsRun - len(result.failures) - len(result.errors)
    }
    
    # Save report
    report_file = Path("test_report.json")
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print("/n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    print(f"Total Tests: {report['total_tests']}")
    print(f"Passed: {report['passed']}")
    print(f"Failures: {report['failures']}")
    print(f"Errors: {report['errors']}")
    print(f"Success Rate: {report['success_rate']:.1f}%")
    print(f"Report saved to: {report_file}")
    
    return report

if __name__ == "__main__":
    run_comprehensive_tests()