"""
Logging setup for Telegram Channel Cloner
Configures logging to both file and console with proper formatting.
"""

import logging
import os
from datetime import datetime
from typing import Optional
from logging.handlers import RotatingFileHandler


def setup_logger(log_level: str = 'INFO', log_file: str = 'telegram_cloner.log') -> logging.Logger:
    """
    Setup logger with both file and console handlers.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Path to log file
        
    Returns:
        Configured logger instance
    """
    # Create logger
    logger = logging.getLogger('telegram_cloner')
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    simple_formatter = logging.Formatter(
        fmt='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    
    # File handler with rotation
    try:
        # Create logs directory if it doesn't exist
        log_dir = os.path.dirname(log_file) or '.'
        os.makedirs(log_dir, exist_ok=True)
        
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        print(f"Warning: Could not setup file logging: {e}")
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, log_level.upper()))
    console_handler.setFormatter(simple_formatter)
    logger.addHandler(console_handler)
    
    # Add startup message
    logger.info("=" * 50)
    logger.info("Telegram Channel Cloner Started")
    logger.info(f"Log Level: {log_level}")
    logger.info(f"Log File: {log_file}")
    logger.info("=" * 50)
    
    return logger


class ProgressLogger:
    """Helper class for logging progress with different levels."""
    
    def __init__(self, logger: logging.Logger, name: str = "Progress"):
        """
        Initialize progress logger.
        
        Args:
            logger: Main logger instance
            name: Name for this progress logger
        """
        self.logger = logger
        self.name = name
        self.start_time = datetime.now()
        self.last_update = self.start_time
        
    def update(self, current: int, total: int, message: str = ""):
        """
        Log progress update.
        
        Args:
            current: Current progress
            total: Total items
            message: Additional message
        """
        now = datetime.now()
        percentage = (current / total) * 100 if total > 0 else 0
        
        # Calculate timing
        elapsed = now - self.start_time
        elapsed_seconds = elapsed.total_seconds()
        
        # Calculate ETA
        if current > 0 and elapsed_seconds > 0:
            rate = current / elapsed_seconds
            remaining = total - current
            eta_seconds = remaining / rate if rate > 0 else 0
            eta = f"{int(eta_seconds // 60)}:{int(eta_seconds % 60):02d}"
        else:
            eta = "Unknown"
        
        # Log message
        progress_msg = f"{self.name}: {current}/{total} ({percentage:.1f}%) - ETA: {eta}"
        if message:
            progress_msg += f" - {message}"
            
        self.logger.info(progress_msg)
        self.last_update = now
    
    def finish(self, message: str = "Completed"):
        """
        Log completion message.
        
        Args:
            message: Completion message
        """
        elapsed = datetime.now() - self.start_time
        elapsed_str = f"{int(elapsed.total_seconds() // 60)}:{int(elapsed.total_seconds() % 60):02d}"
        
        self.logger.info(f"{self.name}: {message} in {elapsed_str}")


def log_exception(logger: logging.Logger, exception: Exception, context: str = ""):
    """
    Log exception with full context.
    
    Args:
        logger: Logger instance
        exception: Exception to log
        context: Additional context information
    """
    error_msg = f"Exception occurred"
    if context:
        error_msg += f" in {context}"
    error_msg += f": {type(exception).__name__}: {str(exception)}"
    
    logger.error(error_msg, exc_info=True)


def log_telegram_error(logger: logging.Logger, error, message_id: Optional[int] = None):
    """
    Log Telegram-specific errors with appropriate handling.
    
    Args:
        logger: Logger instance
        error: Telegram error
        message_id: Message ID if applicable
    """
    error_type = type(error).__name__
    error_msg = str(error)
    
    base_msg = f"Telegram API Error ({error_type}): {error_msg}"
    if message_id:
        base_msg += f" [Message ID: {message_id}]"
    
    # Different log levels for different error types
    if 'FloodWait' in error_type:
        logger.warning(base_msg)
    elif 'Unauthorized' in error_type or 'Forbidden' in error_type:
        logger.error(base_msg)
    elif 'NotFound' in error_type:
        logger.warning(base_msg)
    else:
        logger.error(base_msg, exc_info=True)
