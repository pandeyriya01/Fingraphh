"""
FinGraph Centralized Logging Utility
Provides structured logger across all modules with Windows UTF-8 encoding support.
"""

import os
import sys
import logging

def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(os.getenv("LOG_LEVEL", "INFO").upper())
        formatter = logging.Formatter(
            '[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        # Wrap stdout in utf-8 wrapper if needed on Windows
        if sys.platform == "win32":
            import io
            stream = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        else:
            stream = sys.stdout

        stream_handler = logging.StreamHandler(stream)
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)
    return logger
