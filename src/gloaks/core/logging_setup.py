import logging
import sys
import structlog
from typing import Optional

def configure_logging(level: str = "INFO", log_format: str = "json", log_file: Optional[str] = None):
    """Configure structured logging for the application."""
    
    # Set up standard library logging first
    logging.basicConfig(level=level, format="%(message)s")
    
    shared_processors = [
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    if log_format == "json":
        processors = shared_processors + [structlog.processors.JSONRenderer()]
    else:
        processors = shared_processors + [structlog.dev.ConsoleRenderer()]

    structlog.configure(
        processors=processors,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # If a file is provided, add a file handler to root logger
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        # Use JSON formatter for file logs strictly
        formatter = structlog.stdlib.ProcessorFormatter(
            processor=structlog.processors.JSONRenderer(),
        )
        file_handler.setFormatter(formatter)
        logging.getLogger().addHandler(file_handler)

    logger = structlog.get_logger()
    logger.info("Logging initialized", level=level, format=log_format)
