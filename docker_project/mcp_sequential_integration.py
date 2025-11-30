#!/usr/bin/env python3
"""
MCP Sequential Thinking Integration for AgentDaf1.1
Integrates Docker-based Sequential Thinking MCP server
"""

import json
import requests
import asyncio
import subprocess
try:
    import docker
    from docker.models.containers import Container
except ImportError:
    docker = None
    Container = None
from datetime import datetime
from typing import Dict, List, Any, Optional

class MCPSequentialThinking:
    def __init__(self, docker_container_name="mcp-sequential-thinking"):
        self.container_name = docker_container_name
        self.base_url = "http://localhost:3010"  # Port from docker-compose
        self.client: Optional[Any] = None
        self.container: Optional[Any] = None
        
    async def initialize(self):
        """Initialize MCP connection and Docker container"""
        try:
            # Initialize Docker client
            if docker:
                self.client = docker.from_env()
                
                # Check if container is running
                try:
                    self.container = self.client.containers.get(self.container_name)
                    if self.container and hasattr(self.container, 'status') and self.container.status != 'running':
                        logger.info(f"🔄 Starting {self.container_name} container...")
                        if hasattr(self.container, 'start'):
                            self.container.start()
                        await asyncio.sleep(5)  # Wait for startup
                    else:
                        logger.info(f"✅ {self.container_name} already running")
                except Exception as container_error:
                    logger.info(f"❌ Container {self.container_name} not found: {container_error}")
                    logger.info("Please run: docker-compose up -d sequential-thinking")
                    return False
            else:
                logger.info("⚠️ Docker not available, using direct connection")
            
            # Test MCP server health
            health = await self.check_health()
            if health:
                logger.info("✅ MCP Sequential Thinking server is healthy")
                return True
            else:
                logger.info("❌ MCP Sequential Thinking server is not responding")
                return False
                
        except Exception as e:
            logger.info(f"❌ Failed to initialize MCP: {e}")
            return False
    
    async def check_health(self) -> bool:
        """Check if MCP server is healthy"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    async def process_sequential_thinking(self, prompt: str, context: Optional[Dict] = None) -> Dict:
        """Process prompt using sequential thinking"""
        try:
            payload = {
                "prompt": prompt,
                "context": context or {},
                "timestamp": datetime.now().isoformat(),
                "options": {
                    "max_steps": 5,
                    "include_reasoning": True,
                    "confidence_threshold": 0.7
                }
            }
            
            logger.info(f"🧠 Processing sequential thinking: {prompt[:50]}...")
            
            response = requests.post(
                f"{self.base_url}/api/think",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info("✅ Sequential thinking completed")
                return result
            else:
                logger.info(f"❌ MCP Error: {response.status_code}")
                return {"error": f"HTTP {response.status_code}"}
                
        except requests.exceptions.Timeout:
            logger.info("⏰ Sequential thinking timed out")
            return {"error": "Request timeout"}
        except Exception as e:
            logger.info(f"❌ Sequential thinking failed: {e}")
            return {"error": str(e)}
    
    async def analyze_gaming_data(self, data: Dict) -> Dict:
        """Analyze gaming dashboard data using sequential thinking"""
        prompt = f"""
        Analyze this gaming dashboard data and provide insights:
        
        Total Players: {data.get('total_players', 0)}
        Total Alliances: {data.get('total_alliances', 0)}
        Top Player: {data.get('top_player', 'N/A')}
        Average Score: {data.get('average_score', 0)}
        
        Please provide:
        1. Performance trends analysis
        2. Alliance dynamics insights
        3. Strategic recommendations
        4. Predictions for next ranking period
        """
        
        return await self.process_sequential_thinking(prompt, {"data_type": "gaming_analytics"})
    
    async def predict_player_performance(self, player_data: Dict) -> Dict:
        """Predict player performance using sequential thinking"""
        prompt = f"""
        Analyze player performance and predict future trends:
        
        Player: {player_data.get('name', 'Unknown')}
        Current Score: {player_data.get('score', 0)}
        Alliance: {player_data.get('alliance', 'None')}
        Position: {player_data.get('position', 0)}
        
        Provide:
        1. Performance trend analysis
        2. Improvement recommendations
        3. Predicted next position
        4. Strategic advice
        """
        
        return await self.process_sequential_thinking(prompt, {"data_type": "player_prediction"})
    
    async def analyze_alliance_strategy(self, alliance_data: Dict) -> Dict:
        """Analyze alliance strategy using sequential thinking"""
        prompt = f"""
        Analyze alliance strategy and dynamics:
        
        Alliance: {alliance_data.get('name', 'Unknown')}
        Members: {alliance_data.get('member_count', 0)}
        Total Score: {alliance_data.get('total_score', 0)}
        Average Score: {alliance_data.get('average_score', 0)}
        
        Provide:
        1. Alliance strength analysis
        2. Recruitment recommendations
        3. Strategic positioning
        4. Competitive advantages
        """
        
        return await self.process_sequential_thinking(prompt, {"data_type": "alliance_strategy"})
    
    def get_container_logs(self, lines: int = 50) -> str:
        """Get container logs for debugging"""
        try:
            if self.container:
                logs = self.container.logs(tail=lines)
                return logs.decode('utf-8')
        except Exception as e:
            return f"Error getting logs: {e}"
        return "No container available"
    
    def restart_container(self):
        """Restart the MCP container"""
        try:
            if self.container:
                self.container.restart()
                logger.info(f"🔄 Restarted {self.container_name}")
                return True
        except Exception as e:
            logger.info(f"❌ Failed to restart container: {e}")
            return False
    
    async def test_integration(self) -> Dict:
        """Test full MCP integration"""
        logger.info("🧪 Testing MCP Sequential Thinking integration...")
        
        test_results = {
            "timestamp": datetime.now().isoformat(),
            "tests": []
        }
        
        # Test 1: Health check
        health = await self.check_health()
        test_results["tests"].append({
            "name": "Health Check",
            "status": "PASS" if health else "FAIL",
            "details": "Server is responding" if health else "Server not responding"
        })
        
        # Test 2: Simple thinking
        simple_result = await self.process_sequential_thinking("Test prompt: 2+2=?")
        test_results["tests"].append({
            "name": "Simple Thinking",
            "status": "PASS" if "error" not in simple_result else "FAIL",
            "details": simple_result.get("result", "Failed")[:100]
        })
        
        # Test 3: Complex analysis
        complex_result = await self.analyze_gaming_data({
            "total_players": 100,
            "total_alliances": 10,
            "top_player": "TestPlayer",
            "average_score": 50000
        })
        test_results["tests"].append({
            "name": "Complex Analysis",
            "status": "PASS" if "error" not in complex_result else "FAIL",
            "details": "Gaming data analysis completed" if "error" not in complex_result else "Analysis failed"
        })
        
        return test_results

# CLI Interface
async def main():
    """CLI interface for MCP Sequential Thinking"""
    mcp = MCPSequentialThinking()
    
    if not await mcp.initialize():
        logger.info("❌ Failed to initialize MCP Sequential Thinking")
        return
    
    logger.info("/n🧠 MCP Sequential Thinking - Interactive Mode")
    logger.info("Commands:")
    logger.info("  analyze <json_data> - Analyze gaming data")
    logger.info("  predict <json_data> - Predict player performance")
    logger.info("  strategy <json_data> - Analyze alliance strategy")
    logger.info("  think <prompt> - Custom sequential thinking")
    print("  test - Run integration tests")
    logger.info("  logs - Show container logs")
    logger.info("  restart - Restart container")
    logger.info("  quit - Exit")
    
    while True:
        try:
            command = input("/n🧠 mcp> ").strip()
            
            if not command:
                continue
                
            if command == "quit":
                break
            elif command == "test":
                results = await mcp.test_integration()
                logger.info(json.dumps(results, indent=2))
            elif command == "logs":
                logger.info(mcp.get_container_logs())
            elif command == "restart":
                mcp.restart_container()
            elif command.startswith("think "):
                prompt = command[6:]
                result = await mcp.process_sequential_thinking(prompt)
                logger.info(json.dumps(result, indent=2))
            elif command.startswith("analyze "):
                try:
                    data = json.loads(command[8:])
                    result = await mcp.analyze_gaming_data(data)
                    logger.info(json.dumps(result, indent=2))
                except json.JSONDecodeError:
                    logger.info("❌ Invalid JSON data")
            elif command.startswith("predict "):
                try:
                    data = json.loads(command[8:])
                    result = await mcp.predict_player_performance(data)
                    logger.info(json.dumps(result, indent=2))
                except json.JSONDecodeError:
                    logger.info("❌ Invalid JSON data")
            elif command.startswith("strategy "):
                try:
                    data = json.loads(command[9:])
                    result = await mcp.analyze_alliance_strategy(data)
                    logger.info(json.dumps(result, indent=2))
                except json.JSONDecodeError:
                    logger.info("❌ Invalid JSON data")
            else:
                logger.info("❌ Unknown command. Type 'quit' to exit.")
                
        except KeyboardInterrupt:
            logger.info("/n👋 Goodbye!")
            break
        except Exception as e:
            logger.info(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())