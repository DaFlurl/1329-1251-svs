#!/usr/bin/env python3
"""
AgentDaf1.1 Auto-Repair Script
Automatically detects and fixes common system issues
"""

import asyncio
import subprocess
import sys
import time
import json
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
import docker
from datetime import datetime

# Configure logging
def setup_safe_logging():
    """Setup logging with proper input validation and error handling"""
    log_file = 'auto_repair.log'
    log_dir = os.path.dirname(log_file)
    
    try:
        # Ensure log directory exists
        if not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
            logger.info(f"Created log directory: {log_dir}")
        
        # Validate log file path and permissions
        log_file_path = os.path.abspath(log_file)
        test_file = os.path.join(log_dir, 'test_write.tmp')
        
        # Test write permissions
        try:
            with open(test_file, 'w') as f:
                f.write('test')
            os.remove(test_file)
            logger.info(f"Write permissions confirmed for: {log_file_path}")
        except (IOError, OSError) as e:
            logger.info(f"ERROR: Cannot write to log directory {log_dir}: {e}")
            # Fallback to console-only logging
            return logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(levelname)s - %(message)s',
                handlers=[logging.StreamHandler(sys.stdout)]
            )
        
        # Create FileHandler with validated path
        file_handler = logging.FileHandler(log_file_path)
        file_handler.setLevel(logging.INFO)
        
        return logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                file_handler,
                logging.StreamHandler(sys.stdout)
            ]
        )
    
    except Exception as e:
        logger.info(f"CRITICAL: Failed to setup logging: {e}")
        # Emergency fallback
        return logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[logging.StreamHandler(sys.stdout)]
        )

# Then replace line 23 with:
setup_safe_logging()
logger = logging.getLogger(__name__)

class AutoRepairSystem:
    """Comprehensive auto-repair system for AgentDaf1.1"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.issues_found = []
        self.issues_fixed = []
        self.docker_client = None
        
        try:
            self.docker_client = docker.from_env()
        except Exception as e:
            logger.warning(f"Docker client initialization failed: {e}")
    
    async def run_full_diagnosis(self) -> Dict[str, Any]:
        """Run complete system diagnosis"""
        logger.info("🔍 Starting full system diagnosis...")
        
        diagnosis = {
            "timestamp": datetime.now().isoformat(),
            "checks": {},
            "summary": {"issues": 0, "critical": 0, "warnings": 0}
        }
        
        # Check Docker services
        diagnosis["checks"]["docker_services"] = await self.check_docker_services()
        
        # Check Python dependencies
        diagnosis["checks"]["python_deps"] = await self.check_python_dependencies()
        
        # Check code syntax
        diagnosis["checks"]["syntax"] = await self.check_code_syntax()
        
        # Check configuration files
        diagnosis["checks"]["config"] = await self.check_configuration()
        
        # Check network connectivity
        diagnosis["checks"]["network"] = await self.check_network_connectivity()
        
        # Calculate summary
        for check_name, check_result in diagnosis["checks"].items():
            if check_result.get("issues"):
                diagnosis["summary"]["issues"] += len(check_result["issues"])
                diagnosis["summary"]["critical"] += len([i for i in check_result["issues"] if i.get("severity") == "critical"])
                diagnosis["summary"]["warnings"] += len([i for i in check_result["issues"] if i.get("severity") == "warning"])
        
        logger.info(f"📊 Diagnosis complete: {diagnosis['summary']['issues']} issues found")
        return diagnosis
    
    async def check_docker_services(self) -> Dict[str, Any]:
        """Check Docker services status"""
        logger.info("🐳 Checking Docker services...")
        
        result = {"status": "checking", "issues": [], "services": {}}
        
        if not self.docker_client:
            result["issues"].append({
                "type": "docker_connection",
                "severity": "critical",
                "message": "Cannot connect to Docker daemon",
                "fix": "Start Docker service and ensure proper permissions"
            })
            return result
        
        expected_services = [
            "agentdaf-rabbitmq", "agentdaf-redis", "agentdaf-postgres",
            "agentdaf-elasticsearch", "agentdaf-kibana", "agentdaf-prometheus",
            "agentdaf-grafana", "agentdaf-jaeger"
        ]
        
        try:
            containers = self.docker_client.containers.list(all=True)
            
        except docker.errors.APIError as e:
            result["issues"].append({
                "type": "docker_api_error",
                "severity": "critical",
                "message": f"Docker API error: {e}",
                "fix": "Check Docker daemon status and API permissions"
            })
        except docker.errors.NotFound as e:
            result["issues"].append({
                "type": "docker_not_found",
                "severity": "critical", 
                "message": f"Docker resource not found: {e}",
                "fix": f"Verify container exists and check Docker daemon"
            })
        except Exception as e:
            result["issues"].append({
                "type": "docker_error",
                "severity": "critical",
                "message": f"Error checking Docker services: {e}",
                "fix": "Check Docker daemon status"
            })
            return result
        
        for service_name in expected_services:
            try:
                container = next((c for c in containers if c.name == service_name), None)
                
                if not container:
                    result["issues"].append({
                        "type": "missing_container",
                        "severity": "critical",
                        "service": service_name,
                        "message": f"Container {service_name} not found",
                        "fix": f"Run: docker-compose -f docker-compose.messaging.yml up -d {service_name.replace('agentdaf-', '')}"
                    })
                    result["services"][service_name] = {"status": "missing"}
                else:
                    status = container.status
                    health_status = container.attrs.get("State", {}).get("Health", {}).get("Status", "unknown")
                    result["services"][service_name] = {
                        "status": status,
                        "health": health_status
                    }
                    
                    if status != "running":
                        result["issues"].append({
                            "type": "container_not_running",
                                "severity": "critical",
                                "service": service_name,
                                "message": f"Container {service_name} is {status}",
                                "fix": f"Run: docker start {service_name}"
                        })
                    elif health_status == "unhealthy":
                        result["issues"].append({
                            "type": "container_unhealthy",
                                "severity": "warning",
                                "service": service_name,
                                "message": f"Container {service_name} is unhealthy",
                                "fix": f"Check logs: docker logs {service_name}"
                        })
                        
            except docker.errors.APIError as e:
                result["issues"].append({
                    "type": "container_access_error",
                        "severity": "critical",
                        "message": f"Error accessing container {service_name}: {e}",
                        "fix": f"Check container permissions and Docker daemon"
                    })
            except docker.errors.NotFound as e:
                result["issues"].append({
                    "type": "container_not_found_error",
                        "severity": "critical",
                        "message": f"Container {service_name} access failed: {e}",
                        "fix": f"Verify container exists and check Docker daemon"
                    })
            except Exception as e:
                result["issues"].append({
                    "type": "container_check_error",
                        "severity": "critical",
                        "message": f"Unexpected error checking {service_name}: {e}",
                        "fix": f"Check Docker logs and container status"
                    })
        
        result["status"] = "complete"
        return result
        
        expected_services = [
            "agentdaf-rabbitmq", "agentdaf-redis", "agentdaf-postgres",
            "agentdaf-elasticsearch", "agentdaf-kibana", "agentdaf-prometheus",
            "agentdaf-grafana", "agentdaf-jaeger"
        ]
        
        try:
            containers = self.docker_client.containers.list(all=True)
            
            for service_name in expected_services:
                container = next((c for c in containers if c.name == service_name), None)
                
                if not container:
                    result["issues"].append({
                        "type": "missing_container",
                        "severity": "critical",
                        "service": service_name,
                        "message": f"Container {service_name} not found",
                        "fix": f"Run: docker-compose -f docker-compose.messaging.yml up -d {service_name.replace('agentdaf-', '')}"
                    })
                    result["services"][service_name] = {"status": "missing"}
                else:
                    status = container.status
                    result["services"][service_name] = {
                        "status": status,
                        "health": container.attrs.get("State", {}).get("Health", {}).get("Status", "unknown")
                    }
                    
                    if status != "running":
                        result["issues"].append({
                            "type": "container_not_running",
                            "severity": "critical",
                            "service": service_name,
                            "message": f"Container {service_name} is {status}",
                            "fix": f"Run: docker start {service_name}"
                        })
                    elif result["services"][service_name]["health"] == "unhealthy":
                        result["issues"].append({
                            "type": "container_unhealthy",
                            "severity": "warning",
                            "service": service_name,
                            "message": f"Container {service_name} is unhealthy",
                            "fix": f"Check logs: docker logs {service_name}"
                        })
        
        except Exception as e:
            result["issues"].append({
                "type": "docker_error",
                "severity": "critical",
                "message": f"Error checking Docker services: {e}",
                "fix": "Check Docker daemon status"
            })
        
        result["status"] = "complete"
        return result
    
    async def check_python_dependencies(self) -> Dict[str, Any]:
        """Check if required Python packages are available for the AI tools."""
        try:
            import importlib.util
            import sys
            from typing import Dict, Any
            
            required_packages = ['pandas', 'openpyxl', 'flask', 'aiohttp', 'asyncio']
            missing_packages = []
            
            for package in required_packages:
                try:
                    importlib.util.find_spec(package)
                except ImportError:
                    missing_packages.append(package)
            
            if missing_packages:
                return {
                    "status": "error",
                    "message": f"Missing required Python packages: {', '.join(missing_packages)}",
                    "fix": f"pip install {' '.join(missing_packages)}",
                    "suggestions": [
                        f"Try: pip install --upgrade {package}",
                        f"Verify Python version: python --version",
                        f"Check virtual environment: pip list"
                    ]
                }
            else:
                return {
                    "status": "success",
                    "message": "All required Python packages are available",
                    "details": {
                        "python_version": sys.version,
                        "installed_packages": required_packages
                    }
                    }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error checking Python dependencies: {e}",
                "fix": "Check Python installation and package names",
                "suggestions": [
                    "Verify Python version compatibility",
                    "Check virtual environment activation",
                    "Run: pip check"
                ]
                }
        
        for service, port in ports_to_check.items():
            try:
                import socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                result_code = sock.connect_ex(('localhost', port))
                sock.close()
                
                if result_code == 0:
                    result["services"][service] = {"status": "accessible", "port": port}
                else:
                    result["services"][service] = {"status": "inaccessible", "port": port}
                    result["issues"].append({
                        "type": "port_inaccessible",
                        "severity": "warning",
                        "service": service,
                        "port": port,
                        "message": f"Cannot connect to {service} on port {port}",
                        "fix": f"Check if {service} container is running"
                    })
            except Exception as e:
                result["services"][service] = {"status": "error", "error": str(e)}
        
        result["status"] = "complete"
        return result
    
    async def auto_fix_issues(self, diagnosis: Dict[str, Any]) -> Dict[str, Any]:
        """Automatically fix detected issues"""
        logger.info("🔧 Starting auto-fix process...")
        
        fix_results = {
            "timestamp": datetime.now().isoformat(),
            "fixes_attempted": 0,
            "fixes_successful": 0,
            "fixes_failed": [],
            "details": {}
        }
        
        for check_name, check_result in diagnosis["checks"].items():
            if not check_result.get("issues"):
                continue
            
            for issue in check_result["issues"]:
                fix_results["fixes_attempted"] += 1
                
                try:
                    success = await self.fix_single_issue(issue)
                    if success:
                        fix_results["fixes_successful"] += 1
                        logger.info(f"✅ Fixed: {issue['message']}")
                    else:
                        fix_results["fixes_failed"].append(issue)
                        logger.warning(f"❌ Failed to fix: {issue['message']}")
                except Exception as e:
                    fix_results["fixes_failed"].append(issue)
                    logger.error(f"💥 Error fixing issue: {e}")
        
        logger.info(f"🎯 Auto-fix complete: {fix_results['fixes_successful']}/{fix_results['fixes_attempted']} issues fixed")
        return fix_results
    
    async def fix_single_issue(self, issue: Dict[str, Any]) -> bool:
        """Fix a single issue"""
        issue_type = issue.get("type")
        
        if issue_type == "missing_package":
            return await self.fix_missing_package(issue["package"])
        
        elif issue_type == "container_not_running":
            return await self.fix_container_not_running(issue["service"])
        
        elif issue_type == "missing_container":
            return await self.fix_missing_container(issue["service"])
        
        elif issue_type == "syntax_error":
            return await self.fix_syntax_error(issue["file"], issue.get("line"))
        
        return False
    
    async def fix_missing_package(self, package: str) -> bool:
        """Install missing Python package"""
        try:
            cmd = [sys.executable, "-m", "pip", "install", package]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            return result.returncode == 0
        except Exception:
            return False
    
    async def fix_container_not_running(self, service: str) -> bool:
        """Start stopped container"""
        try:
            if not self.docker_client:
                return False
            
            container = self.docker_client.containers.get(service)
            container.start()
            
            # Wait a moment and check if it's running
            await asyncio.sleep(3)
            container.reload()
            return container.status == "running"
        except Exception:
            return False
    
    async def fix_missing_container(self, service: str) -> bool:
        """Create missing container using docker-compose"""
        try:
            service_name = service.replace("agentdaf-", "")
            cmd = ["docker-compose", "-f", "docker-compose.messaging.yml", "up", "-d", service_name]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120, cwd=self.project_root)
            return result.returncode == 0
        except Exception:
            return False
    
    async def fix_syntax_error(self, file_path: str, line_num: Optional[int]) -> bool:
        """Attempt to fix common syntax errors"""
        try:
            # This is a placeholder for syntax fixing logic
            # In a real implementation, you might use ast parsing to fix common issues
            logger.info(f"Syntax error detected in {file_path} at line {line_num}")
            return False  # Syntax errors usually require manual intervention
        except Exception:
            return False
    
    async def generate_report(self, diagnosis: Dict[str, Any], fix_results: Optional[Dict[str, Any]] = None) -> str:
        """Generate comprehensive repair report with defensive programming"""
        report = []
        report.append("# AgentDaf1.1 Auto-Repair Report")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Summary section with defensive checks
        summary = diagnosis.get("summary", {})
        report.append("## 📊 Summary")
        report.append(f"- Total Issues: {summary.get('issues', 0)}")
        report.append(f"- Critical Issues: {summary.get('critical', 0)}")
        report.append(f"- Warnings: {summary.get('warnings', 0)}")
        report.append("")
        
        # Issues by category with defensive programming
        checks = diagnosis.get("checks", {})
        for check_name, check_result in checks.items():
            # Skip if no issues found with defensive check
            if not check_result or not isinstance(check_result, dict) or not check_result.get("issues"):
                continue
                
            # Add section header with error handling
            try:
                formatted_name = check_name.replace('_', ' ').title()
                report.append(f"## 🔍 {formatted_name}")
            except Exception as e:
                report.append(f"## 🔍 {check_name}")
                report.append(f"   - Error formatting section name: {str(e)}")
                continue
            
            # Process issues with defensive programming
            issues = check_result.get("issues", [])
            if not isinstance(issues, list):
                report.append(f"   - Error: Issues data is not a list")
                continue
                
            for issue in issues:
                # Defensive issue processing
                if not isinstance(issue, dict):
                    report.append(f"   - Error: Invalid issue format")
                    continue
                    
                severity = issue.get("severity", "unknown")
                severity_emoji = "🔴" if severity == "critical" else "🟡"
                
                try:
                    issue_type = issue.get("type", "Unknown Issue").replace('_', ' ').title()
                    report.append(f"{severity_emoji} **{issue_type}**")
                except Exception as e:
                    report.append(f"{severity_emoji} **Error Processing Issue**")
                    report.append(f"   - Error: {str(e)}")
                    continue
                
                # Safe message formatting
                message = issue.get("message", "No message provided")
                report.append(f"   - Message: {message}")
                
                # Safe fix formatting
                fix = issue.get("fix", "No fix available")
                report.append(f"   - Fix: {fix}")
                
                report.append("")
        
        # Fix results section with defensive programming
        if fix_results:
            report.append("## 🔧 Auto-Fix Results")
            
            # Defensive fix results processing
            fixes_attempted = fix_results.get("fixes_attempted", 0)
            fixes_successful = fix_results.get("fixes_successful", 0)
            fixes_failed_list = fix_results.get("fixes_failed", [])
            
            report.append(f"- Fixes Attempted: {fixes_attempted}")
            report.append(f"- Fixes Successful: {fixes_successful}")
            
            # Safe failed fixes processing
            if isinstance(fixes_failed_list, list):
                report.append(f"- Fixes Failed: {len(fixes_failed_list)}")
                
                # Process each failed fix with error handling
                for i, failed_fix in enumerate(fixes_failed_list, 1):
                    if isinstance(failed_fix, dict):
                        fix_description = failed_fix.get("description", "Unknown fix")
                        error_msg = failed_fix.get("error", "Unknown error")
                        report.append(f"   - Failed Fix {i}: {fix_description}")
                        report.append(f"     Error: {error_msg}")
                    else:
                        report.append(f"   - Failed Fix {i}: Invalid format")
            else:
                report.append("   - Error: Failed fixes data is not a list")
        
        # Add footer with timestamp
        report.append("")
        report.append("---")
        report.append(f"*Report generated by AgentDaf1.1 Auto-Repair Tool*")
        report.append(f"*Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return "/n".join(report)
    
    async def run_full_repair_cycle(self) -> Dict[str, Any]:
        """Run complete diagnosis and repair cycle"""
        logger.info("🚀 Starting full repair cycle...")
        
        # Run diagnosis
        diagnosis = await self.run_full_diagnosis()
        
        # Auto-fix issues
        if diagnosis["summary"]["issues"] > 0:
            fix_results = await self.auto_fix_issues(diagnosis)
        else:
            fix_results = {"fixes_attempted": 0, "fixes_successful": 0, "fixes_failed": []}
        
        # Generate report
        report = await self.generate_report(diagnosis, fix_results)
        
        # Save report
        report_path = self.project_root / "repair_report.md"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        logger.info(f"📄 Report saved to: {report_path}")
        
        return {
            "diagnosis": diagnosis,
            "fix_results": fix_results,
            "report_path": str(report_path)
        }

async def main():
    """Main entry point"""
    logger.info("AgentDaf1.1 Auto-Repair System")
    logger.info("=" * 50)
    
    repair_system = AutoRepairSystem()
    
    try:
        results = await repair_system.run_full_repair_cycle()
        
        logger.info("/n🎉 Repair cycle completed!")
        logger.info(f"📊 Issues found: {results['diagnosis']['summary']['issues']}")
        logger.info(f"🔧 Fixes successful: {results['fix_results']['fixes_successful']}")
        logger.info(f"📄 Report: {results['report_path']}")
        
    except KeyboardInterrupt:
        logger.info("/n⏹️ Repair cycle interrupted by user")
    except Exception as e:
        logger.info(f"/n💥 Repair cycle failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())