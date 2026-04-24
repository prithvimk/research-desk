import logging
import sys

def get_logger(name: str) -> logging.Logger:
    """
    Creates and configures a centralized logger.
    """
    logger = logging.getLogger(name)
    
    # Avoid adding handlers multiple times if get_logger is called repeatedly
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        
        # Create console handler
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        
        # Add handler to logger
        logger.addHandler(ch)
        
    return logger
