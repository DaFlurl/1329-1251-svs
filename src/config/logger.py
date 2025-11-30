"""
Advanced Logger Tool for AgentDaf1.1
Structured logging with multiple outputs and formats
"""

import logging
import json
import sys
import os
import time
import threading
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
from pathlib import Path
from datetime import datetime
from enum import Enum
import gzip

class LogLevel(Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

@dataclass
class LogEntry:
    """Structured log entry"""
    timestamp: float
    level: str
    message: str
    module: str
    function: str
    line: int
    thread_id: int
    process_id: int
    extra_data: Optional[Dict[str, Any]] = None
    correlation_id: Optional[str] = None

class StructuredFormatter(logging.Formatter):
    """Custom structured log formatter"""
    
    def __init__(self, include_extra: bool = True):
        super().__init__()
        self.include_extra = include_extra
    
    def format(self, record):
        log_entry = LogEntry(
            timestamp=record.created,
            level=record.levelname,
            message=record.getMessage(),
            module=record.module,
            function=record.funcName,
            line=record.lineno,
            thread_id=record.thread or 0,
            process_id=record.process or 0,
            extra_data=getattr(record, 'extra_data', None) if self.include_extra else None,
            correlation_id=getattr(record, 'correlation_id', None)
        )
        
        return json.dumps(asdict(log_entry), default=str)

class ColoredFormatter(logging.Formatter):
    """Colored console formatter"""
    
    COLORS = {
        'DEBUG': '/033[36m',      # Cyan
        'INFO': '/033[32m',       # Green
        'WARNING': '/033[33m',    # Yellow
        'ERROR': '/033[31m',      # Red
        'CRITICAL': '/033[35m',   # Magenta
        'RESET': '/033[0m'        # Reset
    }
    
    def format(self, record):
        color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        reset = self.COLORS['RESET']
        
        timestamp = datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S')
        
        formatted = (
            f"{color}[{timestamp}] {record.levelname:8} "
            f"{record.module}:{record.funcName}:{record.lineno}{reset} "
            f"- {record.getMessage()}"
        )
        
        if hasattr(record, 'correlation_id') and record.correlation_id:
            formatted += f" (cid: {record.correlation_id})"
        
        return formatted

class RotatingFileHandler:
    """Custom rotating file handler with compression"""
    
    def __init__(self, 
                 filename: str, 
                 max_bytes: int = 10 * 1024 * 1024,  # 10MB
                 backup_count: int = 5,
                 compress: bool = True):
        self.filename = filename
        self.max_bytes = max_bytes
        self.backup_count = backup_count
        self.compress = compress
        self.current_size = 0
        
        # Create directory if needed
        Path(filename).parent.mkdir(parents=True, exist_ok=True)
        
        # Get current file size
        if Path(filename).exists():
            self.current_size = Path(filename).stat().st_size
    
    def should_rotate(self) -> bool:
        """Check if file should be rotated"""
        return self.current_size >= self.max_bytes
    
    def rotate(self):
        """Rotate log files"""
        try:
            # Remove oldest backup if needed
            oldest_backup = f"{self.filename}.{self.backup_count}"
            if Path(oldest_backup).exists():
                Path(oldest_backup).unlink()
            
            # Shift existing backups
            for i in range(self.backup_count - 1, 0, -1):
                old_file = f"{self.filename}.{i}"
                new_file = f"{self.filename}.{i + 1}"
                if Path(old_file).exists():
                    if self.compress and i == 1:
                        # Compress the first backup
                        self._compress_file(old_file, new_file + ".gz")
                        Path(old_file).unlink()
                    else:
                        Path(old_file).rename(new_file)
            
            # Move current file to backup
            if Path(self.filename).exists():
                backup_file = f"{self.filename}.1"
                Path(self.filename).rename(backup_file)
                
                if self.compress:
                    self._compress_file(backup_file, backup_file + ".gz")
                    Path(backup_file).unlink()
            
            # Reset current size
            self.current_size = 0
            
        except Exception as e:
            logger.info(f"Error rotating log file: {e}")
    
    def _compress_file(self, source: str, destination: str):
        """Compress file with gzip"""
        try:
            with open(source, 'rb') as f_in:
                with gzip.open(destination, 'wb') as f_out:
                    f_out.writelines(f_in)
        except Exception as e:
            logger.info(f"Error compressing file: {e}")
    
    def write(self, message: str):
        """Write message to file"""
        try:
            with open(self.filename, 'a', encoding='utf-8') as f:
                f.write(message + '/n')
                f.flush()
            
            self.current_size += len(message.encode('utf-8')) + 1
            
            if self.should_rotate():
                self.rotate()
                
        except Exception as e:
            logger.info(f"Error writing to log file: {e}")

class AdvancedLogger:
    """Advanced logging system with multiple outputs"""
    
    def __init__(self, 
                 name: str = "AgentDaf1.1",
                 log_level: LogLevel = LogLevel.INFO,
                 log_dir: str = "logs",
                 enable_console: bool = True,
                 enable_file: bool = True,
                 enable_structured: bool = False,
                 enable_rotation: bool = True):
        
        self.name = name
        self.log_level = log_level
        self.log_dir = Path(log_dir)
        self.enable_console = enable_console
        self.enable_file = enable_file
        self.enable_structured = enable_structured
        self.enable_rotation = enable_rotation
        
        # Create log directory
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, log_level.value))
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # Setup handlers
        self._setup_handlers()
        
        # Thread safety
        self._lock = threading.Lock()
        
        # Correlation ID management
        self._correlation_context = threading.local()
    
    def _setup_handlers(self):
        """Setup log handlers"""
        
        # Console handler
        if self.enable_console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(ColoredFormatter())
            self.logger.addHandler(console_handler)
        
        # File handler
        if self.enable_file:
            log_file = self.log_dir / f"{self.name.lower().replace(' ', '_')}.log"
            
            if self.enable_rotation:
                file_handler = RotatingFileHandler(str(log_file))
                # Create a custom handler that uses our RotatingFileHandler
                class CustomHandler(logging.Handler):
                    def __init__(self, rotating_handler):
                        super().__init__()
                        self.rotating_handler = rotating_handler
                    
                    def emit(self, record):
                        try:
                            message = self.format(record)
                            self.rotating_handler.write(message)
                        except Exception:
                            self.handleError(record)
                
                custom_handler = CustomHandler(file_handler)
                custom_handler.setFormatter(StructuredFormatter() if self.enable_structured else logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(funcName)s:%(lineno)d - %(message)s'
                ))
                self.logger.addHandler(custom_handler)
            else:
                file_handler = logging.FileHandler(log_file)
                file_handler.setFormatter(StructuredFormatter() if self.enable_structured else logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(funcName)s:%(lineno)d - %(message)s'
                ))
                self.logger.addHandler(file_handler)
    
    def set_correlation_id(self, correlation_id: str):
        """Set correlation ID for current thread"""
        self._correlation_context.correlation_id = correlation_id
    
    def get_correlation_id(self) -> Optional[str]:
        """Get correlation ID for current thread"""
        return getattr(self._correlation_context, 'correlation_id', None)
    
    def clear_correlation_id(self):
        """Clear correlation ID for current thread"""
        if hasattr(self._correlation_context, 'correlation_id'):
            delattr(self._correlation_context, 'correlation_id')
    
    def _log(self, level: LogLevel, message: str, extra_data: Dict[str, Any] = None):
        """Internal logging method"""
        with self._lock:
            extra = {
                'extra_data': extra_data,
                'correlation_id': self.get_correlation_id()
            }
            
            self.logger.log(getattr(logging, level.value), message, extra=extra)
    
    def debug(self, message: str, **kwargs):
        """Log debug message"""
        self._log(LogLevel.DEBUG, message, kwargs)
    
    def info(self, message: str, **kwargs):
        """Log info message"""
        self._log(LogLevel.INFO, message, kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message"""
        self._log(LogLevel.WARNING, message, kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message"""
        self._log(LogLevel.ERROR, message, kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log critical message"""
        self._log(LogLevel.CRITICAL, message, kwargs)
    
    def log_function_call(self, func_name: str, args: tuple = (), kwargs: dict = None):
        """Log function call with parameters"""
        self.debug(f"Calling {func_name}", 
                  args=str(args), 
                  kwargs=str(kwargs or {}))
    
    def log_performance(self, operation: str, duration: float, **metrics):
        """Log performance metrics"""
        self.info(f"Performance: {operation}", 
                 duration_seconds=duration, 
                 **metrics)
    
    def log_api_request(self, method: str, endpoint: str, status_code: int, 
                       duration: float, **kwargs):
        """Log API request"""
        self.info(f"API Request: {method} {endpoint}", 
                 status_code=status_code, 
                 duration_ms=duration * 1000,
                 **kwargs)
    
    def log_error_with_traceback(self, message: str, exception: Exception):
        """Log error with full traceback"""
        import traceback
        self.error(message, 
                 exception_type=type(exception).__name__,
                 exception_message=str(exception),
                 traceback=traceback.format_exc())
    
    def get_log_stats(self) -> Dict[str, Any]:
        """Get logging statistics"""
        try:
            log_file = self.log_dir / f"{self.name.lower().replace(' ', '_')}.log"
            
            if not log_file.exists():
                return {"error": "Log file not found"}
            
            stats = log_file.stat()
            
            # Count log levels
            level_counts = {level.value: 0 for level in LogLevel}
            
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        for level in LogLevel:
                            if level.value in line:
                                level_counts[level.value] += 1
                                break
            except Exception:
                pass
            
            return {
                "file_size_bytes": stats.st_size,
                "file_size_mb": stats.st_size / 1024 / 1024,
                "created_at": stats.st_ctime,
                "modified_at": stats.st_mtime,
                "level_counts": level_counts,
                "total_entries": sum(level_counts.values())
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def search_logs(self, 
                   pattern: str, 
                   level: LogLevel = None,
                   hours: int = 24,
                   max_results: int = 100) -> List[Dict[str, Any]]:
        """Search logs for pattern"""
        try:
            log_file = self.log_dir / f"{self.name.lower().replace(' ', '_')}.log"
            
            if not log_file.exists():
                return []
            
            cutoff_time = time.time() - (hours * 3600)
            results = []
            
            with open(log_file, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    try:
                        # Parse timestamp from log line
                        if self.enable_structured:
                            log_data = json.loads(line.strip())
                            timestamp = log_data.get('timestamp', 0)
                            log_level = log_data.get('level', '')
                            message = log_data.get('message', '')
                        else:
                            # Simple timestamp extraction
                            parts = line.split(' - ')
                            if len(parts) >= 3:
                                time_str = parts[0].strip('[]')
                                try:
                                    timestamp = datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S').timestamp()
                                except:
                                    timestamp = 0
                                log_level = parts[1].strip() if len(parts) > 1 else ''
                                message = ' - '.join(parts[2:])
                            else:
                                continue
                        
                        # Check filters
                        if timestamp < cutoff_time:
                            continue
                        
                        if level and log_level != level.value:
                            continue
                        
                        if pattern.lower() not in message.lower():
                            continue
                        
                        results.append({
                            "line_number": line_num,
                            "timestamp": timestamp,
                            "level": log_level,
                            "message": message,
                            "raw_line": line.strip()
                        })
                        
                        if len(results) >= max_results:
                            break
                            
                    except Exception:
                        continue
            
            return results
            
        except Exception as e:
            return [{"error": str(e)}]

# Global logger instances
loggers: Dict[str, AdvancedLogger] = {}

def get_logger(name: str = "AgentDaf1.1", **kwargs) -> AdvancedLogger:
    """Get or create logger instance"""
    if name not in loggers:
        loggers[name] = AdvancedLogger(name, **kwargs)
    return loggers[name]

def setup_logging(log_level: LogLevel = LogLevel.INFO, **kwargs):
    """Setup default logging configuration"""
    return get_logger("AgentDaf1.1", log_level=log_level, **kwargs)