"""
Reusable logging utility for the Trading Strategy Analysis Platform.

Usage:
    from utils.logger import get_logger

    logger = get_logger(__name__)

    logger.debug("Debug information")
    logger.info("Application started")
    logger.warning("Something unexpected happened")
    logger.error("Something went wrong")
"""

import logging


def get_logger(name: str) -> logging.Logger:
    """
    Return a configured logger for the given module.

    Parameters
    ----------
    name : str
        Module name (typically __name__).

    Returns
    -------
    logging.Logger
        Configured logger instance.
    """

    logger = logging.getLogger(name)

    # Prevent duplicate handlers if the logger has already been configured.
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)

    # Prevent propagation to the root logger to avoid duplicate messages.
    logger.propagate = False

    return logger