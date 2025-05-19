import logging
from logging.config import dictConfig

def setup_logging():
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "()": "uvicorn.logging.DefaultFormatter",
                "fmt": "%(levelprefix)s %(asctime)s | %(name)s | %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "error": {
                "format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s"
            }
        },
        "handlers": {
            "default": {
                "formatter": "default",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
            },
            "error_file": {
                "level": "ERROR",
                "formatter": "error",
                "class": "logging.FileHandler",
                "filename": "errors.log",
            }
        },
        "root": {
            "handlers": ["default", "error_file"],
            "level": "INFO",
        },
        "loggers": {
            "uvicorn.error": {
                "level": "INFO",
                "handlers": ["default", "error_file"],
                "propagate": False,
            },
            "uvicorn.access": {
                "handlers": ["default"],
                "level": "INFO",
                "propagate": False,
            },
        },
    }

    dictConfig(logging_config)
