import asyncio
import threading
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from enum import Enum
import json
import logging
from pathlib import Path

class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class TaskPriority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    URGENT = 4

class Task:
    def __init__(self, name: str, func: Callable, args: tuple = (), kwargs: Optional[Dict[str, Any]] = None, 
                  priority: TaskPriority = TaskPriority.MEDIUM, timeout: int = 300):
        self.id = str(uuid.uuid4())
        self.name = name
        self.func = func
        self.args = args
        self.kwargs = kwargs or {}
        self.priority = priority
        self.timeout = timeout
        self.status = TaskStatus.PENDING
        self.created_at = datetime.now()
        self.started_at = None
        self.completed_at = None
        self.result = None
        self.error = None
        self.progress = 0
        self.logs = []

class TaskManager:
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.tasks: Dict[str, Task] = {}
        self.task_queue: List[str] = []
        self.running_tasks: Dict[str, threading.Thread] = {}
        self.workers_available = max_workers
        self.is_running = False
        self.logger = logging.getLogger('agentdaf1.task_manager')
        
        # Task storage
        self.storage_dir = Path('data/tasks')
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        # Start task processor
        self.start_processor()
    
    def add_task(self, name: str, func: Callable, args: tuple = (), kwargs: dict = None,
                 priority: TaskPriority = TaskPriority.MEDIUM, timeout: int = 300) -> str:
        """Add a new task to the queue"""
        task = Task(name, func, args, kwargs, priority, timeout)
        self.tasks[task.id] = task
        
        # Insert task based on priority
        inserted = False
        for i, task_id in enumerate(self.task_queue):
            existing_task = self.tasks[task_id]
            if priority.value > existing_task.priority.value:
                self.task_queue.insert(i, task.id)
                inserted = True
                break
        
        if not inserted:
            self.task_queue.append(task.id)
        
        self.logger.info(f"Task added: {name} (ID: {task.id})")
        self.save_task(task)
        return task.id
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """Get task by ID"""
        return self.tasks.get(task_id)
    
    def get_tasks(self, status: Optional[TaskStatus] = None) -> List[Task]:
        """Get all tasks, optionally filtered by status"""
        tasks = list(self.tasks.values())
        if status:
            tasks = [t for t in tasks if t.status == status]
        return sorted(tasks, key=lambda x: x.created_at, reverse=True)
    
    def cancel_task(self, task_id: str) -> bool:
        """Cancel a task"""
        task = self.tasks.get(task_id)
        if not task:
            return False
        
        if task.status == TaskStatus.RUNNING:
            # Can't cancel running tasks (would need more complex implementation)
            return False
        
        task.status = TaskStatus.CANCELLED
        if task_id in self.task_queue:
            self.task_queue.remove(task_id)
        
        self.logger.info(f"Task cancelled: {task.name} (ID: {task_id})")
        self.save_task(task)
        return True
    
    def update_task_progress(self, task_id: str, progress: int, message: str = ""):
        """Update task progress"""
        task = self.tasks.get(task_id)
        if task:
            task.progress = min(100, max(0, progress))
            if message:
                task.logs.append(f"{datetime.now().strftime('%H:%M:%S')}: {message}")
            self.save_task(task)
    
    def start_processor(self):
        """Start the task processor thread"""
        if not self.is_running:
            self.is_running = True
            processor_thread = threading.Thread(target=self._process_tasks, daemon=True)
            processor_thread.start()
            self.logger.info("Task processor started")
    
    def stop_processor(self):
        """Stop the task processor"""
        self.is_running = False
        self.logger.info("Task processor stopped")
    
    def _process_tasks(self):
        """Process tasks from the queue"""
        while self.is_running:
            try:
                # Check for available workers
                if self.workers_available > 0 and self.task_queue:
                    task_id = self.task_queue.pop(0)
                    task = self.tasks.get(task_id)
                    
                    if task and task.status == TaskStatus.PENDING:
                        # Start task in new thread
                        self.workers_available -= 1
                        thread = threading.Thread(
                            target=self._execute_task,
                            args=(task_id,),
                            daemon=True
                        )
                        self.running_tasks[task_id] = thread
                        thread.start()
                
                # Clean up completed threads
                completed_tasks = []
                for task_id, thread in self.running_tasks.items():
                    if not thread.is_alive():
                        completed_tasks.append(task_id)
                
                for task_id in completed_tasks:
                    del self.running_tasks[task_id]
                    self.workers_available += 1
                
                time.sleep(0.1)  # Small delay to prevent busy waiting
                
            except Exception as e:
                self.logger.error(f"Error in task processor: {str(e)}")
                time.sleep(1)
    
    def _execute_task(self, task_id: str):
        """Execute a single task"""
        task = self.tasks.get(task_id)
        if not task:
            return
        
        try:
            task.status = TaskStatus.RUNNING
            task.started_at = datetime.now()
            self.save_task(task)
            
            self.logger.info(f"Executing task: {task.name} (ID: {task_id})")
            
            # Execute with timeout
            if task.timeout > 0:
                result = self._execute_with_timeout(task)
            else:
                result = task.func(*task.args, **task.kwargs)
            
            task.result = result
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now()
            task.progress = 100
            
            self.logger.info(f"Task completed: {task.name} (ID: {task_id})")
            
        except Exception as e:
            task.error = str(e)
            task.status = TaskStatus.FAILED
            task.completed_at = datetime.now()
            task.logs.append(f"Error: {str(e)}")
            
            self.logger.error(f"Task failed: {task.name} (ID: {task_id}) - {str(e)}")
        
        finally:
            self.save_task(task)
    
    def _execute_with_timeout(self, task: Task) -> Any:
        """Execute task with timeout using threading"""
        result_container = {}
        exception_container = {}
        
        def target():
            try:
                result_container['result'] = task.func(*task.args, **task.kwargs)
            except Exception as e:
                exception_container['exception'] = e
        
        thread = threading.Thread(target=target)
        thread.start()
        thread.join(timeout=task.timeout)
        
        if thread.is_alive():
            # Task timed out
            raise TimeoutError(f"Task timed out after {task.timeout} seconds")
        
        if 'exception' in exception_container:
            raise exception_container['exception']
        
        return result_container['result']
    
    def save_task(self, task: Task):
        """Save task to file"""
        try:
            task_data = {
                'id': task.id,
                'name': task.name,
                'status': task.status.value,
                'priority': task.priority.value,
                'progress': task.progress,
                'created_at': task.created_at.isoformat(),
                'started_at': task.started_at.isoformat() if task.started_at else None,
                'completed_at': task.completed_at.isoformat() if task.completed_at else None,
                'result': str(task.result) if task.result is not None else None,
                'error': task.error,
                'logs': task.logs,
                'timeout': task.timeout
            }
            
            file_path = self.storage_dir / f"{task.id}.json"
            with open(file_path, 'w') as f:
                json.dump(task_data, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Error saving task {task.id}: {str(e)}")
    
    def load_tasks(self):
        """Load tasks from storage"""
        try:
            for file_path in self.storage_dir.glob("*.json"):
                with open(file_path, 'r') as f:
                    task_data = json.load(f)
                
                # Recreate task object
                task = Task(
                    name=task_data['name'],
                    func=lambda: None,  # Placeholder
                    priority=TaskPriority(task_data['priority']),
                    timeout=task_data.get('timeout', 300)
                )
                
                task.id = task_data['id']
                task.status = TaskStatus(task_data['status'])
                task.progress = task_data.get('progress', 0)
                task.created_at = datetime.fromisoformat(task_data['created_at'])
                task.started_at = datetime.fromisoformat(task_data['started_at']) if task_data.get('started_at') else None
                task.completed_at = datetime.fromisoformat(task_data['completed_at']) if task_data.get('completed_at') else None
                task.result = task_data.get('result')
                task.error = task_data.get('error')
                task.logs = task_data.get('logs', [])
                
                self.tasks[task.id] = task
                
        except Exception as e:
            self.logger.error(f"Error loading tasks: {str(e)}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get task statistics"""
        total_tasks = len(self.tasks)
        status_counts = {}
        
        for status in TaskStatus:
            status_counts[status.value] = len([t for t in self.tasks.values() if t.status == status])
        
        return {
            'total_tasks': total_tasks,
            'status_counts': status_counts,
            'queue_length': len(self.task_queue),
            'running_tasks': len(self.running_tasks),
            'workers_available': self.workers_available,
            'max_workers': self.max_workers
        }
    
    def cleanup_old_tasks(self, days: int = 7):
        """Clean up old completed tasks"""
        cutoff_date = datetime.now() - timedelta(days=days)
        tasks_to_remove = []
        
        for task_id, task in self.tasks.items():
            if (task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED] and
                task.completed_at and task.completed_at < cutoff_date):
                tasks_to_remove.append(task_id)
        
        for task_id in tasks_to_remove:
            task = self.tasks[task_id]
            del self.tasks[task_id]
            
            # Remove file
            file_path = self.storage_dir / f"{task_id}.json"
            if file_path.exists():
                file_path.unlink()
            
            # Remove from queue if present
            if task_id in self.task_queue:
                self.task_queue.remove(task_id)
        
        self.logger.info(f"Cleaned up {len(tasks_to_remove)} old tasks")
        return len(tasks_to_remove)

# Global task manager instance
task_manager = TaskManager()

def get_task_manager() -> TaskManager:
    """Get global task manager instance"""
    return task_manager