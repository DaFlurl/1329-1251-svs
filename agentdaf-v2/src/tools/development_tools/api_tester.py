#!/usr/bin/env python3
"""
AgentDaf1.1 - API Tester Tool
Automated API testing and documentation generation
"""

import json
import time
import requests
import threading
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
import logging
import sqlite3
import concurrent.futures
from urllib.parse import urljoin

class APITester:
    """Automated API testing and documentation generation"""
    
    def __init__(self):
        self.name = "API Tester"
        self.version = "1.0.0"
        self.logger = logging.getLogger(__name__)
        self.lock = threading.Lock()
        
        # Project paths
        self.project_root = Path(__file__).parent.parent.parent.parent
        self.api_test_db_path = self.project_root / "data" / "api_tests.db"
        
        # Ensure data directory exists
        self.api_test_db_path.parent.mkdir(exist_ok=True)
        
        # API testing configuration
        self.config = {
            "default_timeout": 30,
            "max_retries": 3,
            "concurrent_requests": 10,
            "load_test_duration": 60,  # seconds
            "expected_status_codes": [200, 201, 202, 204],
            "performance_thresholds": {
                "response_time_ms": 1000,
                "throughput_rps": 100
            }
        }
        
        # Initialize API test database
        self._init_api_test_db()
        
        self.logger.info(f"API Tester initialized: {self.name} v{self.version}")
    
    def _init_api_test_db(self):
        """Initialize API test database"""
        conn = sqlite3.connect(str(self.api_test_db_path))
        conn.execute('''
            CREATE TABLE IF NOT EXISTS api_endpoints (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                url TEXT NOT NULL,
                method TEXT NOT NULL,
                headers TEXT,
                body TEXT,
                expected_status INTEGER DEFAULT 200,
                timeout INTEGER,
                created_at REAL
            )
        ''')
        
        conn.execute('''
            CREATE TABLE IF NOT EXISTS test_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                endpoint_id INTEGER,
                test_type TEXT NOT NULL,
                status_code INTEGER,
                response_time_ms REAL,
                response_size INTEGER,
                success BOOLEAN,
                error_message TEXT,
                timestamp REAL,
                FOREIGN KEY (endpoint_id) REFERENCES api_endpoints (id)
            )
        ''')
        
        conn.execute('''
            CREATE TABLE IF NOT EXISTS load_test_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                endpoint_id INTEGER,
                total_requests INTEGER,
                successful_requests INTEGER,
                failed_requests INTEGER,
                avg_response_time_ms REAL,
                min_response_time_ms REAL,
                max_response_time_ms REAL,
                requests_per_second REAL,
                duration_seconds REAL,
                timestamp REAL,
                FOREIGN KEY (endpoint_id) REFERENCES api_endpoints (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_endpoint(self, endpoint_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add API endpoint for testing"""
        try:
            # Validate required fields
            required_fields = ["name", "url", "method"]
            for field in required_fields:
                if field not in endpoint_data:
                    return {"success": False, "error": f"Missing required field: {field}"}
            
            # Set defaults
            endpoint_data.setdefault("headers", {})
            endpoint_data.setdefault("body", None)
            endpoint_data.setdefault("expected_status", 200)
            endpoint_data.setdefault("timeout", self.config["default_timeout"])
            endpoint_data.setdefault("created_at", time.time())
            
            # Save to database
            conn = sqlite3.connect(str(self.api_test_db_path))
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO api_endpoints 
                (name, url, method, headers, body, expected_status, timeout, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                endpoint_data["name"],
                endpoint_data["url"],
                endpoint_data["method"].upper(),
                json.dumps(endpoint_data["headers"]),
                json.dumps(endpoint_data["body"]) if endpoint_data["body"] else None,
                endpoint_data["expected_status"],
                endpoint_data["timeout"],
                endpoint_data["created_at"]
            ))
            
            endpoint_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            endpoint_data["id"] = endpoint_id
            
            return {
                "success": True,
                "endpoint_id": endpoint_id,
                "endpoint": endpoint_data
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def test_endpoint(self, endpoint_id: int, test_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Test a single API endpoint"""
        try:
            # Get endpoint from database
            conn = sqlite3.connect(str(self.api_test_db_path))
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM api_endpoints WHERE id = ?", (endpoint_id,))
            row = cursor.fetchone()
            conn.close()
            
            if not row:
                return {"success": False, "error": "Endpoint not found"}
            
            endpoint = {
                "id": row[0],
                "name": row[1],
                "url": row[2],
                "method": row[3],
                "headers": json.loads(row[4]) if row[4] else {},
                "body": json.loads(row[5]) if row[5] else None,
                "expected_status": row[6],
                "timeout": row[7]
            }
            
            # Override with test data if provided
            if test_data:
                endpoint.update(test_data)
            
            # Perform the test
            start_time = time.time()
            
            try:
                response = requests.request(
                    method=endpoint["method"],
                    url=endpoint["url"],
                    headers=endpoint["headers"],
                    json=endpoint["body"] if endpoint["body"] and endpoint["method"] in ["POST", "PUT", "PATCH"] else None,
                    timeout=endpoint["timeout"],
                    verify=False  # For testing purposes
                )
                
                response_time_ms = (time.time() - start_time) * 1000
                response_size = len(response.content)
                success = response.status_code == endpoint["expected_status"]
                
                result = {
                    "endpoint_id": endpoint_id,
                    "test_type": "single",
                    "status_code": response.status_code,
                    "response_time_ms": response_time_ms,
                    "response_size": response_size,
                    "success": success,
                    "response_headers": dict(response.headers),
                    "response_body": response.text[:1000] if response.text else None,  # Truncate for storage
                    "timestamp": time.time()
                }
                
                if not success:
                    result["error_message"] = f"Expected status {endpoint['expected_status']}, got {response.status_code}"
                
                # Save result to database
                self._save_test_result(result)
                
                return {"success": True, "result": result}
                
            except requests.exceptions.RequestException as e:
                response_time_ms = (time.time() - start_time) * 1000
                
                result = {
                    "endpoint_id": endpoint_id,
                    "test_type": "single",
                    "status_code": None,
                    "response_time_ms": response_time_ms,
                    "response_size": 0,
                    "success": False,
                    "error_message": str(e),
                    "timestamp": time.time()
                }
                
                # Save result to database
                self._save_test_result(result)
                
                return {"success": True, "result": result}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def test_all_endpoints(self) -> Dict[str, Any]:
        """Test all configured endpoints"""
        try:
            # Get all endpoints
            conn = sqlite3.connect(str(self.api_test_db_path))
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM api_endpoints")
            endpoint_ids = [row[0] for row in cursor.fetchall()]
            conn.close()
            
            if not endpoint_ids:
                return {"success": False, "error": "No endpoints configured"}
            
            # Test endpoints concurrently
            results = []
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.config["concurrent_requests"]) as executor:
                future_to_endpoint = {
                    executor.submit(self.test_endpoint, endpoint_id): endpoint_id 
                    for endpoint_id in endpoint_ids
                }
                
                for future in concurrent.futures.as_completed(future_to_endpoint):
                    endpoint_id = future_to_endpoint[future]
                    try:
                        result = future.result()
                        results.append(result)
                    except Exception as e:
                        results.append({
                            "success": False,
                            "endpoint_id": endpoint_id,
                            "error": str(e)
                        })
            
            # Calculate summary
            successful_tests = sum(1 for r in results if r.get("success"))
            failed_tests = len(results) - successful_tests
            
            return {
                "success": True,
                "total_endpoints": len(endpoint_ids),
                "successful_tests": successful_tests,
                "failed_tests": failed_tests,
                "results": results
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def load_test_endpoint(self, endpoint_id: int, config: Dict[str, Any] = None) -> Dict[str, Any]:
        """Perform load testing on an endpoint"""
        try:
            # Get endpoint
            conn = sqlite3.connect(str(self.api_test_db_path))
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM api_endpoints WHERE id = ?", (endpoint_id,))
            row = cursor.fetchone()
            conn.close()
            
            if not row:
                return {"success": False, "error": "Endpoint not found"}
            
            endpoint = {
                "id": row[0],
                "name": row[1],
                "url": row[2],
                "method": row[3],
                "headers": json.loads(row[4]) if row[4] else {},
                "body": json.loads(row[5]) if row[5] else None,
                "expected_status": row[6],
                "timeout": row[7]
            }
            
            # Load test configuration
            load_config = {
                "duration": config.get("duration", self.config["load_test_duration"]),
                "concurrent_users": config.get("concurrent_users", 10),
                "ramp_up_time": config.get("ramp_up_time", 10)
            }
            
            # Perform load test
            start_time = time.time()
            results = []
            
            def make_request():
                try:
                    req_start = time.time()
                    response = requests.request(
                        method=endpoint["method"],
                        url=endpoint["url"],
                        headers=endpoint["headers"],
                        json=endpoint["body"] if endpoint["body"] and endpoint["method"] in ["POST", "PUT", "PATCH"] else None,
                        timeout=endpoint["timeout"],
                        verify=False
                    )
                    req_time = (time.time() - req_start) * 1000
                    
                    return {
                        "success": response.status_code == endpoint["expected_status"],
                        "response_time_ms": req_time,
                        "status_code": response.status_code
                    }
                except:
                    return {
                        "success": False,
                        "response_time_ms": 0,
                        "status_code": None
                    }
            
            # Run load test
            with concurrent.futures.ThreadPoolExecutor(max_workers=load_config["concurrent_users"]) as executor:
                end_time = start_time + load_config["duration"]
                
                while time.time() < end_time:
                    futures = [executor.submit(make_request) for _ in range(load_config["concurrent_users"])]
                    for future in concurrent.futures.as_completed(futures):
                        results.append(future.result())
                    
                    time.sleep(1)  # Wait 1 second between batches
            
            # Calculate metrics
            total_requests = len(results)
            successful_requests = sum(1 for r in results if r["success"])
            failed_requests = total_requests - successful_requests
            
            response_times = [r["response_time_ms"] for r in results if r["success"]]
            avg_response_time = sum(response_times) / len(response_times) if response_times else 0
            min_response_time = min(response_times) if response_times else 0
            max_response_time = max(response_times) if response_times else 0
            
            actual_duration = time.time() - start_time
            requests_per_second = total_requests / actual_duration if actual_duration > 0 else 0
            
            load_result = {
                "endpoint_id": endpoint_id,
                "total_requests": total_requests,
                "successful_requests": successful_requests,
                "failed_requests": failed_requests,
                "avg_response_time_ms": avg_response_time,
                "min_response_time_ms": min_response_time,
                "max_response_time_ms": max_response_time,
                "requests_per_second": requests_per_second,
                "duration_seconds": actual_duration,
                "success_rate_percent": (successful_requests / total_requests * 100) if total_requests > 0 else 0,
                "timestamp": time.time()
            }
            
            # Save load test result
            self._save_load_test_result(load_result)
            
            return {"success": True, "result": load_result}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def generate_api_documentation(self, endpoint_ids: List[int] = None) -> Dict[str, Any]:
        """Generate API documentation from endpoints"""
        try:
            # Get endpoints
            conn = sqlite3.connect(str(self.api_test_db_path))
            cursor = conn.cursor()
            
            if endpoint_ids:
                placeholders = ','.join(['?' for _ in endpoint_ids])
                cursor.execute(f"SELECT * FROM api_endpoints WHERE id IN ({placeholders})", endpoint_ids)
            else:
                cursor.execute("SELECT * FROM api_endpoints")
            
            rows = cursor.fetchall()
            conn.close()
            
            if not rows:
                return {"success": False, "error": "No endpoints found"}
            
            # Generate documentation
            documentation = {
                "title": "API Documentation",
                "version": "1.0.0",
                "generated_at": datetime.now().isoformat(),
                "endpoints": []
            }
            
            for row in rows:
                endpoint = {
                    "id": row[0],
                    "name": row[1],
                    "url": row[2],
                    "method": row[3],
                    "headers": json.loads(row[4]) if row[4] else {},
                    "body": json.loads(row[5]) if row[5] else None,
                    "expected_status": row[6],
                    "timeout": row[7]
                }
                
                # Get recent test results for this endpoint
                test_results = self._get_endpoint_test_results(endpoint["id"], limit=5)
                
                endpoint_doc = {
                    "name": endpoint["name"],
                    "method": endpoint["method"],
                    "url": endpoint["url"],
                    "description": f"API endpoint for {endpoint['name']}",
                    "headers": endpoint["headers"],
                    "body_example": endpoint["body"],
                    "expected_status": endpoint["expected_status"],
                    "recent_performance": {
                        "avg_response_time": sum(r["response_time_ms"] for r in test_results) / len(test_results) if test_results else 0,
                        "success_rate": sum(1 for r in test_results if r["success"]) / len(test_results) if test_results else 0,
                        "last_tested": test_results[0]["timestamp"] if test_results else None
                    }
                }
                
                documentation["endpoints"].append(endpoint_doc)
            
            return {"success": True, "documentation": documentation}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _save_test_result(self, result: Dict[str, Any]):
        """Save test result to database"""
        conn = sqlite3.connect(str(self.api_test_db_path))
        conn.execute('''
            INSERT INTO test_results 
            (endpoint_id, test_type, status_code, response_time_ms, response_size, success, error_message, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            result["endpoint_id"],
            result["test_type"],
            result["status_code"],
            result["response_time_ms"],
            result["response_size"],
            result["success"],
            result.get("error_message"),
            result["timestamp"]
        ))
        conn.commit()
        conn.close()
    
    def _save_load_test_result(self, result: Dict[str, Any]):
        """Save load test result to database"""
        conn = sqlite3.connect(str(self.api_test_db_path))
        conn.execute('''
            INSERT INTO load_test_results 
            (endpoint_id, total_requests, successful_requests, failed_requests, 
             avg_response_time_ms, min_response_time_ms, max_response_time_ms, 
             requests_per_second, duration_seconds, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            result["endpoint_id"],
            result["total_requests"],
            result["successful_requests"],
            result["failed_requests"],
            result["avg_response_time_ms"],
            result["min_response_time_ms"],
            result["max_response_time_ms"],
            result["requests_per_second"],
            result["duration_seconds"],
            result["timestamp"]
        ))
        conn.commit()
        conn.close()
    
    def _get_endpoint_test_results(self, endpoint_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent test results for an endpoint"""
        conn = sqlite3.connect(str(self.api_test_db_path))
        cursor = conn.cursor()
        cursor.execute('''
            SELECT status_code, response_time_ms, success, timestamp 
            FROM test_results 
            WHERE endpoint_id = ? 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (endpoint_id, limit))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                "status_code": row[0],
                "response_time_ms": row[1],
                "success": bool(row[2]),
                "timestamp": row[3]
            })
        
        conn.close()
        return results
    
    def get_endpoints(self) -> Dict[str, Any]:
        """Get all configured endpoints"""
        conn = sqlite3.connect(str(self.api_test_db_path))
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM api_endpoints ORDER BY created_at DESC")
        
        columns = [desc[0] for desc in cursor.description]
        endpoints = []
        
        for row in cursor.fetchall():
            endpoint = dict(zip(columns, row))
            # Parse JSON fields
            if endpoint["headers"]:
                endpoint["headers"] = json.loads(endpoint["headers"])
            if endpoint["body"]:
                endpoint["body"] = json.loads(endpoint["body"])
            endpoints.append(endpoint)
        
        conn.close()
        
        return {
            "success": True,
            "endpoints": endpoints,
            "total": len(endpoints)
        }
    
    def get_test_results(self, endpoint_id: int = None, limit: int = 50) -> Dict[str, Any]:
        """Get test results"""
        conn = sqlite3.connect(str(self.api_test_db_path))
        cursor = conn.cursor()
        
        if endpoint_id:
            cursor.execute('''
                SELECT * FROM test_results 
                WHERE endpoint_id = ? 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (endpoint_id, limit))
        else:
            cursor.execute('''
                SELECT * FROM test_results 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (limit,))
        
        columns = [desc[0] for desc in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        
        return {
            "success": True,
            "results": results,
            "total": len(results)
        }
    
    def delete_endpoint(self, endpoint_id: int) -> Dict[str, Any]:
        """Delete an endpoint"""
        try:
            conn = sqlite3.connect(str(self.api_test_db_path))
            
            # Delete endpoint and related results
            cursor = conn.cursor()
            cursor.execute("DELETE FROM test_results WHERE endpoint_id = ?", (endpoint_id,))
            cursor.execute("DELETE FROM load_test_results WHERE endpoint_id = ?", (endpoint_id,))
            cursor.execute("DELETE FROM api_endpoints WHERE id = ?", (endpoint_id,))
            
            deleted = cursor.rowcount > 0
            conn.commit()
            conn.close()
            
            if deleted:
                return {"success": True, "endpoint_id": endpoint_id}
            else:
                return {"success": False, "error": "Endpoint not found"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_status(self) -> Dict[str, Any]:
        """Get API tester status"""
        # Get statistics
        conn = sqlite3.connect(str(self.api_test_db_path))
        
        # Endpoint count
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM api_endpoints")
        endpoint_count = cursor.fetchone()[0]
        
        # Test results summary
        cursor.execute('''
            SELECT COUNT(*), AVG(response_time_ms), 
                   SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful,
                   SUM(CASE WHEN success = 0 THEN 1 ELSE 0 END) as failed
            FROM test_results 
            WHERE timestamp > ?
        ''', (time.time() - 86400,))  # Last 24 hours
        
        recent_stats = cursor.fetchone()
        
        conn.close()
        
        return {
            "name": self.name,
            "version": self.version,
            "status": "active",
            "endpoints_configured": endpoint_count,
            "recent_24h": {
                "total_tests": recent_stats[0] or 0,
                "avg_response_time_ms": recent_stats[1] or 0,
                "successful": recent_stats[2] or 0,
                "failed": recent_stats[3] or 0
            },
            "config": self.config,
            "timestamp": datetime.now().isoformat()
        }

# Global instance
api_tester = APITester()