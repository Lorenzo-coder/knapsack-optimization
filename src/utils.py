"""
Utility functions for Knapsack Optimization Pipeline.
Includes logging setup, input validation, and error handling.
"""

import logging
import json
import os
import signal
import contextlib
import gc
from typing import Dict, Optional, Any
from config import (
    LOG_LEVEL, LOG_FORMAT, LOG_TO_FILE, LOG_TO_CONSOLE,
    DEBUG_MODE, ENABLE_GARBAGE_COLLECTION
)


class TimeoutError(Exception):
    """Raised when an operation exceeds timeout."""
    pass


def setup_logging(output_dir: str) -> logging.Logger:
    """
    Configure logging for the pipeline.
    
    Args:
        output_dir: Directory where log file will be saved
        
    Returns:
        Configured logger instance
    """
    from config import LOG_FILE
    
    log_file = os.path.join(output_dir, LOG_FILE)
    
    logger = logging.getLogger("KnapsackPipeline")
    logger.setLevel(getattr(logging, LOG_LEVEL))
    
    formatter = logging.Formatter(LOG_FORMAT)
    
    # Console handler
    if LOG_TO_CONSOLE:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # File handler
    if LOG_TO_FILE:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


@contextlib.contextmanager
def timeout(seconds: int):
    """
    Context manager for operation timeout (Unix-like systems).
    
    Args:
        seconds: Timeout duration in seconds
        
    Raises:
        TimeoutError: If operation exceeds timeout
    """
    def timeout_handler(signum, frame):
        raise TimeoutError(f"Operation timeout after {seconds}s")
    
    # Set alarm signal
    old_handler = signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(seconds)
    
    try:
        yield
    finally:
        signal.alarm(0)  # Cancel alarm
        signal.signal(signal.SIGALRM, old_handler)


def load_and_validate_instance(filepath: str) -> Optional[Dict[str, Any]]:
    """
    Load and validate a Knapsack instance from JSON file.
    
    Args:
        filepath: Path to JSON file
        
    Returns:
        Validated data dictionary or None if invalid
    """
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        logging.warning(f"Malformed JSON in {filepath}: {e}")
        return None
    except Exception as e:
        logging.warning(f"Error reading {filepath}: {e}")
        return None
    
    # Validate structure
    required_top_keys = {"sets", "parameters"}
    if not required_top_keys.issubset(data.keys()):
        logging.warning(f"Missing top-level keys in {filepath}")
        return None
    
    # Validate sets
    if "P" not in data["sets"] or not data["sets"]["P"]:
        logging.warning(f"Empty items list in {filepath}")
        return None
    
    # Validate parameters
    required_params = {"b", "C", "a"}
    if not required_params.issubset(data["parameters"].keys()):
        logging.warning(f"Missing parameters in {filepath}")
        return None
    
    # Validate parameter types
    try:
        b = data["parameters"]["b"]
        C = data["parameters"]["C"]
        A = data["parameters"]["a"]
        
        if not isinstance(b, (int, float)) or b <= 0:
            logging.warning(f"Invalid capacity in {filepath}")
            return None
        
        if not isinstance(C, dict) or not C:
            logging.warning(f"Invalid values dict in {filepath}")
            return None
        
        if not isinstance(A, dict) or not A:
            logging.warning(f"Invalid weights dict in {filepath}")
            return None
    
    except (TypeError, KeyError) as e:
        logging.warning(f"Invalid parameter types in {filepath}: {e}")
        return None
    
    return data


def safe_garbage_collection():
    """Perform garbage collection if enabled in config."""
    if ENABLE_GARBAGE_COLLECTION:
        gc.collect()


def get_error_category(exception: Exception) -> str:
    """
    Categorize exception for better error reporting.
    
    Args:
        exception: Exception to categorize
        
    Returns:
        Error category string
    """
    if isinstance(exception, TimeoutError):
        return "TIMEOUT"
    elif isinstance(exception, MemoryError):
        return "MEMORY"
    elif isinstance(exception, ImportError):
        return "DEPENDENCY"
    elif isinstance(exception, KeyError):
        return "INVALID_DATA"
    elif isinstance(exception, ValueError):
        return "VALUE_ERROR"
    else:
        return "UNKNOWN"


def format_error_message(task_name: str, exception: Exception) -> str:
    """
    Format error message with category and details.
    
    Args:
        task_name: Name of the task that failed
        exception: The exception that occurred
        
    Returns:
        Formatted error message
    """
    category = get_error_category(exception)
    return f"[{category}] {task_name}: {str(exception)}"


def get_memory_usage_mb() -> float:
    """
    Get current process memory usage in MB.
    
    Returns:
        Memory usage in megabytes
    """
    import psutil
    return psutil.Process().memory_info().rss / (1024 * 1024)
