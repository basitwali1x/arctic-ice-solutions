import tracemalloc
import psutil
import logging
from functools import wraps
from typing import Callable, Any

def profile_memory_usage(func_name: str):
    """Decorator to profile memory usage of functions"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            tracemalloc.start()
            process = psutil.Process()
            memory_before = process.memory_info().rss / 1024 / 1024  # MB
            
            result = func(*args, **kwargs)
            
            current, peak = tracemalloc.get_traced_memory()
            memory_after = process.memory_info().rss / 1024 / 1024  # MB
            tracemalloc.stop()
            
            logging.info(f"Memory profile for {func_name}: "
                        f"RSS before: {memory_before:.1f}MB, "
                        f"RSS after: {memory_after:.1f}MB, "
                        f"Peak traced: {peak / 1024 / 1024:.1f}MB")
            return result
        return wrapper
    return decorator

def log_memory_usage(operation: str):
    """Log current memory usage for a specific operation"""
    process = psutil.Process()
    memory_mb = process.memory_info().rss / 1024 / 1024
    logging.info(f"Memory usage during {operation}: {memory_mb:.1f}MB")
