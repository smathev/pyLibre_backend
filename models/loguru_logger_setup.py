from loguru import logger
import sys
import logging
from models.utils_path_manager import path_manager

log_file_full_path = path_manager.log_file_full_path

class AppLogger:
    def __init__(self, logger_name, application_name):
        self.logger_name = logger_name
        self.application_name = application_name

        logger.configure(
            handlers=[
                {
                    "sink": sys.stdout,
                    "format": "<yellow>{time:YYYY-MM-DD HH:mm:ss}</yellow> | <level>{level}</level> | <cyan>{name}</cyan> - <level>{message}</level>",
                    "level": "INFO",  # Set minimum logging level to INFO
                    "backtrace": False,  # Disable deep tracebacks
                    "diagnose": False    # Disable detailed variable inspection
                },
                {
                    "sink": log_file_full_path,
                    "rotation": "1 day",
                    "retention": "6 days",
                    "format": "{time:YYYY-MM-DD HH:mm:ss}, {level}, filename: {name}, message: {message}",
                    "backtrace": False,  # Disable deep tracebacks
                    "diagnose": False    # Disable detailed variable inspection
                }
            ]
        )

class InterceptHandler(logging.Handler):
    def emit(self, record):
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the log message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


logging.basicConfig(handlers=[InterceptHandler()], level=0)
