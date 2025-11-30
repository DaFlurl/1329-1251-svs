#!/usr/bin/env python3
"""
AgentDaf1.1 Tools Launcher
Master control panel for all system tools and utilities
"""

import asyncio
import sys
import os
from pathlib import Path
import argparse
from typing import Dict, Any

# Add tools directory to path
tools_dir = Path(__file__).parent
sys.path.insert(0, str(tools_dir))

class ToolsLauncher:
    """Master launcher for all AgentDaf1.1 tools"""
    
    def __init__(self):
        self.project_root = tools_dir.parent
        self.tools = {
            "auto-repair": {
                "module": "auto_repair",
                "description": "Automatically detect and fix system issues",
                "function": "main"
            },
            "health-monitor": {
                "module": "health_monitor", 
                "description": "Real-time system health monitoring",
                "function": "main"
            },
            "dependency-manager": {
                "module": "dependency_manager",
                "description": "Install and manage Python dependencies",
                "function": "main"
            }
        }
    
    def list_tools(self):
        """List all available tools"""
        logger.info("🛠️  AgentDaf1.1 Available Tools")
        logger.info("=" * 50)
        
        for name, info in self.tools.items():
            logger.info(f"🔧 {name:20} - {info['description']}")
        
        logger.info("/nUsage: python tools_launcher.py <tool-name> [tool-args]")
        logger.info("Example: python tools_launcher.py auto-repair")
        logger.info("Example: python tools_launcher.py dependency-manager --full-setup")
    
    async def run_tool(self, tool_name: str, args: list = None):
        """Run a specific tool"""
        if tool_name not in self.tools:
            logger.info(f"❌ Unknown tool: {tool_name}")
            self.list_tools()
            return False
        
        tool_info = self.tools[tool_name]
        
        try:
            logger.info(f"🚀 Starting {tool_name}...")
            logger.info(f"📝 Description: {tool_info['description']}")
            logger.info("-" * 50)
            
            # Import and run the tool
            module = __import__(tool_info["module"])
            tool_function = getattr(module, tool_info["function"])
            
            # Prepare arguments for the tool
            if args:
                # Temporarily modify sys.argv for the tool
                original_argv = sys.argv
                sys.argv = [tool_name] + args
                
                try:
                    if asyncio.iscoroutinefunction(tool_function):
                        result = await tool_function()
                    else:
                        result = tool_function()
                finally:
                    sys.argv = original_argv
            else:
                if asyncio.iscoroutinefunction(tool_function):
                    result = await tool_function()
                else:
                    result = tool_function()
            
            logger.info("-" * 50)
            logger.info(f"✅ {tool_name} completed successfully!")
            return True
            
        except ImportError as e:
            logger.info(f"❌ Failed to import {tool_info['module']}: {e}")
            return False
        except AttributeError as e:
            logger.info(f"❌ Function {tool_info['function']} not found: {e}")
            return False
        except KeyboardInterrupt:
            logger.info(f"/n⏹️ {tool_name} interrupted by user")
            return False
        except Exception as e:
            logger.info(f"❌ {tool_name} failed: {e}")
            return False
    
    async def run_system_check(self):
        """Run quick system health check"""
        logger.info("Running quick system health check...")
        
        # Check if critical services are running
        try:
            import docker
            client = docker.from_env()
            
            critical_services = ["agentdaf-rabbitmq", "agentdaf-redis", "agentdaf-postgres"]
            running_services = []
            
            for service in critical_services:
                try:
                    container = client.containers.get(service)
                    if container.status == "running":
                        running_services.append(service)
                        logger.info(f"[OK] {service} is running")
                    else:
                        logger.info(f"❌ {service} is {container.status}")
                except:
                    logger.info(f"❌ {service} not found")
            
            logger.info(f"/n📊 Services: {len(running_services)}/{len(critical_services)} running")
            
            # Check Python dependencies
            critical_deps = ["fastapi", "aio-pika", "redis", "sqlalchemy"]
            missing_deps = []
            
            for dep in critical_deps:
                try:
                    __import__(dep.replace("-", "_"))
                    logger.info(f"✅ {dep} installed")
                except ImportError:
                    missing_deps.append(dep)
                    logger.info(f"❌ {dep} missing")
            
            logger.info(f"/n📦 Dependencies: {len(critical_deps) - len(missing_deps)}/{len(critical_deps)} installed")
            
            # Overall status
            if len(running_services) == len(critical_services) and not missing_deps:
                logger.info("/n🎉 System is healthy!")
                return True
            else:
                logger.info("/n⚠️ System needs attention")
                return False
                
        except ImportError:
            logger.info("❌ Docker not available")
            return False
        except Exception as e:
            logger.info(f"❌ System check failed: {e}")
            return False
    
    async def show_dashboard(self):
        """Show system dashboard"""
        logger.info("📊 AgentDaf1.1 System Dashboard")
        logger.info("=" * 60)
        
        # System status
        health_ok = await self.run_system_check()
        
        logger.info("/n🛠️  Available Actions:")
        logger.info("1. Run auto-repair - Fix detected issues")
        logger.info("2. Run health-monitor - Start continuous monitoring")
        logger.info("3. Run dependency-manager - Manage dependencies")
        logger.info("4. Run system-check - Quick health check")
        logger.info("5. List tools - Show all available tools")
        logger.info("6. Exit")
        
        while True:
            try:
                choice = input("/nEnter choice (1-6): ").strip()
                
                if choice == "1":
                    await self.run_tool("auto-repair")
                elif choice == "2":
                    await self.run_tool("health-monitor")
                elif choice == "3":
                    await self.run_tool("dependency-manager", ["--help"])
                elif choice == "4":
                    await self.run_system_check()
                elif choice == "5":
                    self.list_tools()
                elif choice == "6":
                    logger.info("👋 Goodbye!")
                    break
                else:
                    logger.info("❌ Invalid choice. Please enter 1-6.")
                    
            except KeyboardInterrupt:
                logger.info("/nGoodbye!")
                break
            except Exception as e:
                logger.info(f"Error: {e}")

async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="AgentDaf1.1 Tools Launcher",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Available tools:
  auto-repair        - Automatically detect and fix system issues
  health-monitor     - Real-time system health monitoring  
  dependency-manager - Install and manage Python dependencies

Examples:
  python tools_launcher.py auto-repair
  python tools_launcher.py health-monitor
  python tools_launcher.py dependency-manager --full-setup
  python tools_launcher.py --dashboard
  python tools_launcher.py --check
        """
    )
    
    parser.add_argument("tool", nargs="?", help="Tool to run")
    parser.add_argument("args", nargs="*", help="Arguments for the tool")
    parser.add_argument("--dashboard", action="store_true", help="Show interactive dashboard")
    parser.add_argument("--check", action="store_true", help="Run quick system check")
    parser.add_argument("--list", action="store_true", help="List all available tools")
    
    args = parser.parse_args()
    
    launcher = ToolsLauncher()
    
    try:
        if args.dashboard:
            await launcher.show_dashboard()
        elif args.check:
            success = await launcher.run_system_check()
            sys.exit(0 if success else 1)
        elif args.list:
            launcher.list_tools()
        elif args.tool:
            success = await launcher.run_tool(args.tool, args.args)
            sys.exit(0 if success else 1)
        else:
            parser.print_help()
    
    except KeyboardInterrupt:
        logger.info("/n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        logger.info(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())