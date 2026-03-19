import logging
import sys


def get_logger(name: str) -> logging.Logger:
    """
    Create and return a named logger with consistent formatting.
    Call this at the top of any module that needs logging.

    Usage:
        from core.logger import get_logger
        logger = get_logger(__name__)
        logger.info("Something happened")
    """
    logger = logging.getLogger(name)

    # Avoid adding duplicate handlers if logger is already configured
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # Prevent log messages from propagating to the root logger
    logger.propagate = False

    return logger
