"""Logging configuration for the detection system."""

import logging
import os


def setup_logger(log_file: str, name: str = 'layering_detector') -> logging.Logger:
    """
    Configure logger with console and file output.
    
    Args:
        log_file: Path to log file
        name: Logger name
        
    Returns:
        Configured logger instance
    """
    # Ensure log directory exists
    log_dir = os.path.dirname(log_file)
    if log_dir:
        os.makedirs(log_dir, exist_ok=True)
    
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    # File handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.INFO)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Format: [2024-01-01 10:00:00] INFO: message
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


def log_detection(logger: logging.Logger, account_id: str, product_id: str, 
                  timestamps: list, duration: float):
    """
    Log a suspicious pattern detection.
    
    Args:
        logger: Logger instance
        account_id: Account identifier
        product_id: Product identifier
        timestamps: List of event timestamps
        duration: Pattern duration in seconds
    """
    logger.warning(
        f"SUSPICIOUS: account={account_id}, product={product_id}, "
        f"events={len(timestamps)}, duration={duration:.2f}s"
    )
    logger.info(f"Timestamps: {[str(t) for t in timestamps]}")