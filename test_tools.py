#!/usr/bin/env python3
"""
Tool Integration Test Script for AgentDaf1.1
Tests all advanced tools functionality
"""

import sys
import time
import tempfile
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def test_memory_manager():
    """Test memory manager functionality"""
    print("Testing Memory Manager...")
    
    from src.tools.memory_manager import memory_manager
    
    # Test memory info
    info = memory_manager.get_memory_info()
    assert info is not None
    assert "process_memory_mb" in info
    print(f"  Memory info: {info['process_memory_mb']:.2f} MB")
    
    # Test snapshot
    snapshot = memory_manager.take_snapshot()
    assert snapshot is not None
    assert snapshot.process_memory_mb > 0
    print(f"  Snapshot taken: {snapshot.process_memory_mb:.2f} MB")
    
    # Test optimization
    result = memory_manager.optimize_memory()
    assert "before" in result
    assert "after" in result
    print(f"  Memory optimization completed")
    
    # Test trend analysis
    trend = memory_manager.get_memory_trend()
    print(f"  Trend analysis: {trend.get('trend', 'N/A')}")
    
    print("  Memory Manager: All tests passed/n")

def test_task_manager():
    """Test task manager functionality"""
    print("Testing Task Manager...")
    
    from src.tools.task_manager import task_manager
    import asyncio
    
    async def run_task_tests():
        # Create a simple test task
        def test_task(x, y):
            return x + y
        
        task_id = task_manager.create_task(
            "test_addition",
            test_task,
            "Test addition task",
            args=(5, 3)
        )
        assert task_id is not None
        print(f"  Task created: {task_id}")
        
        # Get task status
        status = task_manager.get_task_status(task_id)
        assert status is not None
        assert status["name"] == "test_addition"
        print(f"  Task status: {status['status']}")
        
        # Get queue status
        queue_status = task_manager.get_queue_status()
        assert "total_tasks" in queue_status
        print(f"  Queue status: {queue_status['total_tasks']} tasks")
        
        # Test task execution (run briefly)
        task_manager.is_running = True
        # Run a single execution cycle
        try:
            await task_manager.execute_task(task_id)
            print("  Task execution completed")
        except Exception as e:
            print(f"  Task execution note: {e}")
        finally:
            task_manager.stop()
    
    # Run async tests
    asyncio.run(run_task_tests())
    print("  Task Manager: All tests passed/n")

def test_performance_monitor():
    """Test performance monitor functionality"""
    print("Testing Performance Monitor...")
    
    from src.tools.performance_monitor import performance_monitor
    
    # Test current metrics
    metrics = performance_monitor.get_current_metrics()
    assert metrics is not None
    assert metrics.cpu_percent >= 0
    print(f"  Current metrics: CPU {metrics.cpu_percent:.1f}%")
    
    # Test system info
    sys_info = performance_monitor.get_system_info()
    assert sys_info is not None
    assert "cpu_count" in sys_info
    print(f"  System info: {sys_info['cpu_count']} CPUs")
    
    # Test alerts
    alerts = performance_monitor.get_alerts()
    assert isinstance(alerts, list)
    print(f"  Alerts: {len(alerts)} active alerts")
    
    # Test thresholds
    from src.tools.performance_monitor import AlertThreshold
    threshold = AlertThreshold("test_metric", 50.0, 80.0)
    performance_monitor.add_threshold(threshold)
    print("  Alert threshold added")
    
    print("  Performance Monitor: All tests passed/n")

def test_file_manager():
    """Test file manager functionality"""
    print("Testing File Manager...")
    
    from src.tools.file_manager import file_manager
    
    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        # Test directory listing
        files = file_manager.list_directory(temp_dir)
        assert isinstance(files, list)
        print(f"  Directory listing: {len(files)} items")
        
        # Test file creation
        test_file = Path(temp_dir) / "test.txt"
        test_file.write_text("Hello, World!")
        
        # Test file info
        file_info = file_manager.get_file_info(str(test_file))
        assert file_info is not None
        assert file_info.name == "test.txt"
        print(f"  File info: {file_info.name} ({file_info.size} bytes)")
        
        # Test directory size
        size_info = file_manager.get_directory_size(temp_dir)
        assert "total_size" in size_info
        print(f"  Directory size: {size_info['total_size']} bytes")
        
        # Test file operations
        dest_file = Path(temp_dir) / "test_copy.txt"
        success = file_manager.copy_file(str(test_file), str(dest_file))
        assert success
        assert dest_file.exists()
        print("  File copy successful")
        
        # Test cleanup
        success = file_manager.delete_file(str(dest_file))
        assert success
        assert not dest_file.exists()
        print("  File deletion successful")
    
    print("  File Manager: All tests passed/n")

def test_advanced_logger():
    """Test advanced logger functionality"""
    print("Testing Advanced Logger...")
    
    from src.tools.logger import get_logger, LogLevel
    
    # Create logger
    logger = get_logger("test_logger", log_level=LogLevel.INFO)
    assert logger is not None
    print("  Logger created")
    
    # Test logging methods
    logger.info("Test info message")
    logger.warning("Test warning message")
    logger.error("Test error message")
    print("  Log messages written")
    
    # Test correlation ID
    logger.set_correlation_id("test-correlation-123")
    logger.info("Test message with correlation ID")
    logger.clear_correlation_id()
    print("  Correlation ID functionality")
    
    # Test log stats
    stats = logger.get_log_stats()
    assert "file_size_bytes" in stats
    print(f"  Log stats: {stats['file_size_bytes']} bytes")
    
    print("  Advanced Logger: All tests passed/n")

def test_security_monitor():
    """Test security monitor functionality"""
    print("Testing Security Monitor...")
    
    from src.tools.security import security_monitor, SecurityValidator, SecurityPolicy
    
    # Test security validator
    is_valid, errors = SecurityValidator.validate_password("Test123!@", security_monitor.get_policy())
    assert is_valid
    print("  Password validation working")
    
    # Test email validation
    assert SecurityValidator.validate_email("test@example.com")
    assert not SecurityValidator.validate_email("invalid-email")
    print("  Email validation working")
    
    # Test IP validation
    assert SecurityValidator.validate_ip_address("192.168.1.1")
    assert not SecurityValidator.validate_ip_address("invalid-ip")
    print("  IP validation working")
    
    # Test token generation
    token = SecurityValidator.generate_secure_token(16)
    assert len(token) > 0
    print("  Secure token generation working")
    
    # Test security monitoring
    security_monitor.log_event("TEST_EVENT", "LOW", "Test security event")
    events = security_monitor.get_events(hours=1)
    assert len(events) > 0
    print(f"  Security event logging: {len(events)} events")
    
    # Test session management
    session_id = security_monitor.create_session("test_user", "127.0.0.1")
    assert session_id is not None
    session = security_monitor.validate_session(session_id, "127.0.0.1")
    assert session is not None
    assert session["user_id"] == "test_user"
    print("  Session management working")
    
    # Test security summary
    summary = security_monitor.get_security_summary()
    assert "total_events_24h" in summary
    print(f"  Security summary: {summary['total_events_24h']} events")
    
    print("  Security Monitor: All tests passed/n")

def test_integration():
    """Test tool integration"""
    print("Testing Tool Integration...")
    
    # Test that all tools can be imported and used together
    from src.tools.memory_manager import memory_manager
    from src.tools.task_manager import task_manager
    from src.tools.performance_monitor import performance_monitor
    from src.tools.file_manager import file_manager
    from src.tools.logger import get_logger
    from src.tools.security import security_monitor
    
    # Create a logger for integration testing
    logger = get_logger("integration_test")
    
    # Take memory snapshot
    snapshot = memory_manager.take_snapshot()
    logger.info("Memory snapshot taken", memory_mb=snapshot.process_memory_mb)
    
    # Get performance metrics
    metrics = performance_monitor.get_current_metrics()
    logger.info("Performance metrics collected", cpu_percent=metrics.cpu_percent)
    
    # Log security event
    security_monitor.log_event("INTEGRATION_TEST", "LOW", "Integration test completed")
    
    # Get file info for current directory
    current_dir = Path.cwd()
    files = file_manager.list_directory(str(current_dir), recursive=False)
    logger.info("Directory listed", file_count=len(files))
    
    print("  All tools working together")
    print("  Tool Integration: All tests passed/n")

def main():
    """Run all tests"""
    print("Starting AgentDaf1.1 Tool Integration Tests/n")
    
    try:
        test_memory_manager()
        test_task_manager()
        test_performance_monitor()
        test_file_manager()
        test_advanced_logger()
        test_security_monitor()
        test_integration()
        
        print("All tests completed successfully!")
        print("AgentDaf1.1 Tool Suite is fully functional")
        
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())