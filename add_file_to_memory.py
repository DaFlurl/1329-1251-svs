#!/usr/bin/env python3
"""
Add test file to neural memory system
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def add_file_to_memory():
    try:
        from tools.neural_memory import NeuralMemorySystem
        
        # Initialize memory system
        memory = NeuralMemorySystem()
        logger.info("Memory system initialized")
        
        # Read the test file
        with open("test_memory_file.txt", "r") as f:
            file_content = f.read()
        
        logger.info(f"File content read: {len(file_content)} characters")
        
        # Add to working memory (active task)
        memory.add_to_working_memory("file_processing_task", f"Processing test_memory_file.txt with {len(file_content)} characters")
        logger.info("Added to working memory")
        
        # Add to episodic memory (experience of reading the file)
        memory.add_to_episodic_memory(
            content="Read and processed test_memory_file.txt",
            context={
                "action": "file_read",
                "filename": "test_memory_file.txt",
                "size": len(file_content),
                "timestamp": "2025-11-27",
                "purpose": "memory_system_testing"
            },
            importance=0.8
        )
        logger.info("Added to episodic memory")
        
        # Add to semantic memory (knowledge about the file)
        memory.add_to_semantic_memory(
            content={
                "description": "Test file for neural memory system",
                "components": ["Working Memory", "Episodic Memory", "Semantic Memory"],
                "purpose": "Demonstrate memory system capabilities",
                "created_date": "2025-11-27"
            },
            category="test_file",
            relationships=["memory_system", "testing", "demonstration"]
        )
        logger.info("Added to semantic memory")
        
        # Search and retrieve memories
        logger.info("/n=== Memory Retrieval ===")
        
        # Working memory
        working = memory.working_memory
        logger.info(f"Working memory items: {len(working)}")
        for item in working:
            logger.info(f"  - {item.content}")
        
        # Episodic memory search
        episodic_results = memory.search_episodic_memory("file", limit=3)
        logger.info(f"/nEpisodic memory results: {len(episodic_results)}")
        for item in episodic_results:
            logger.info(f"  - {item.content} (Context: {item.context})")
        
        # Semantic memory search
        semantic_results = memory.search_semantic_memory("memory", category="test_file")
        logger.info(f"/nSemantic memory results: {len(semantic_results)}")
        for item in semantic_results:
            logger.info(f"  - {item.content} (Category: {item.category})")
        
        # Get memory statistics
        stats = memory.get_memory_stats()
        logger.info(f"/nMemory Statistics: {stats}")
        
        logger.info("/nFile successfully added to memory system!")
        return True
        
    except Exception as e:
        logger.info(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = add_file_to_memory()
    sys.exit(0 if success else 1)