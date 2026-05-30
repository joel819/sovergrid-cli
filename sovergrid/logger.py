"""
SoverGrid Logger
Professional logging with colored terminal output.
No print() statements anywhere in the codebase.
"""

import logging
import sys


# ANSI color codes for terminal output
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"

    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"


class SoverGridFormatter(logging.Formatter):
    """Custom formatter that adds color coding based on log level."""

    LEVEL_COLORS = {
        logging.DEBUG: Colors.DIM + Colors.WHITE,
        logging.INFO: Colors.CYAN,
        logging.WARNING: Colors.YELLOW,
        logging.ERROR: Colors.RED,
        logging.CRITICAL: Colors.BOLD + Colors.RED,
    }

    LEVEL_ICONS = {
        logging.DEBUG: "  ",
        logging.INFO: ">>",
        logging.WARNING: "!!",
        logging.ERROR: "XX",
        logging.CRITICAL: "💀",
    }

    def format(self, record):
        color = self.LEVEL_COLORS.get(record.levelno, Colors.WHITE)
        icon = self.LEVEL_ICONS.get(record.levelno, "  ")
        reset = Colors.RESET

        # Format the prefix with the SoverGrid brand
        prefix = f"{Colors.BOLD}{Colors.MAGENTA}[sovergrid]{reset}"
        level_tag = f"{color}{icon}{reset}"
        message = f"{color}{record.getMessage()}{reset}"

        return f"{prefix} {level_tag} {message}"


def get_logger(name: str = "sovergrid") -> logging.Logger:
    """
    Returns a configured SoverGrid logger instance.

    Usage:
        from sovergrid.logger import get_logger
        log = get_logger(__name__)
        log.info("Deploying to Akash...")
    """
    logger = logging.getLogger(name)

    # Prevent duplicate handlers if called multiple times
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    # Console handler with colored output
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(SoverGridFormatter())

    logger.addHandler(console_handler)

    return logger
