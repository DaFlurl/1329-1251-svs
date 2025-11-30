#!/usr/bin/env python3
"""
Test script for neural memory system
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_memory():
    try:
        from tools.neural_memory import NeuralMemorySystem
        print("Successfully imported NeuralMemorySystem")
        
        # Initialize
        memory = NeuralMemorySystem()
        print("Memory system initialized")
        
        # Test working memory
        memory.add_to_working_memory("test_task", "Test data")
        working = memory.working_memory
        print(f"Working memory: {len(working)} items")
        
        # Test episodic memory
        memory.add_to_episodic_memory("test_episode", {"data": "test"}, importance=0.8)
        episodic = memory.search_episodic_memory("test", limit=5)
        print(f"Episodic memory: {len(episodic)} items")
        
        # Test semantic memory
        memory.add_to_semantic_memory({"definition": "test"}, "test_concept")
        semantic = memory.search_semantic_memory("test", category="test_concept")
        print(f"Semantic memory: {len(semantic)} items")
        
        # Test search
        results = memory.search_working_memory("test")
        print(f"Search found: {len(results)} results")
        
        print("/nMemory system test completed successfully!")
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_memory()
    sys.exit(0 if success else 1)