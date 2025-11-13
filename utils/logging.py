# utils/logging.py
import logging

import colorlog

from config import SETTINGS


def setup_logging() -> logging.Logger:
    """
    Sets up the logger for colored logging.
    Log level is read from settings (LOG_LEVEL).
    """

    # 1. Define the colored format
    log_format = (
        "%(asctime)s [%(levelname)s] [%(name)s] "
        "%(log_color)s%(message)s%(reset)s"
    )

    # 2. Create the colored formatter
    formatter = colorlog.ColoredFormatter(
        log_format,
        log_colors={
            "DEBUG": "cyan",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "red,bg_white",
        },
        reset=True,
        style="%",
    )

    # 3. Create the console handler and set the formatter
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # 4. Get the main logger for the project
    app_logger = logging.getLogger("ai_companion")

    # Set the log level based on configuration
    level = getattr(logging, SETTINGS.LOG_LEVEL.upper(), logging.INFO)
    app_logger.setLevel(level)

    app_logger.addHandler(console_handler)
    app_logger.propagate = False  # Prevent double logging

    return app_logger


# 5. Set up the logger and export it
logger = setup_logging()

# A debug message to verify the new settings
logger.debug("Logger 'ai_companion' initialized with color and configured log level.")
