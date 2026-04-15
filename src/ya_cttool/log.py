from logging import FileHandler
import logging.config

from pythonjsonlogger.json import JsonFormatter

from .config import LoggingConfig

"""
"format": "%(asctime)s : %(levelname)s : %(module)s : %(funcName)s : %(lineno)d : (Process Details : (%(process)d, %(processName)s), Thread Details : (%(thread)d, %(threadName)s))\nLog : %(message)s",
"""

LOGGING_FORMAT = "%(asctime)s | %(levelname)-5s | %(filename)s:%(lineno)d (%(funcName)s)  | %(message)s"

LOGGER_NAME = "yacttool"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "std_out": {
            "format": LOGGING_FORMAT,
            "datefmt": "%d-%m-%Y %I:%M:%S",
        }
    },
    "handlers": {
        "std_out": {
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
            "formatter": "std_out",
            "level": "NOTSET",
        }
    },
    "loggers": {
        LOGGER_NAME: {"handlers": ["std_out"], "level": "NOTSET", "propagate": False}
    },
}


logging.config.dictConfig(LOGGING)


def configure_logger_from_config(config: LoggingConfig, file_path: str):
    """_summary_"""
    stream_lvl = logging.WARNING
    if config.stream_level is not None:
        stream_lvl = _parse_level(config.stream_level)
    set_log_level(stream_lvl)
    enable_file_logging(
        filename=file_path,
        logger_name=LOGGER_NAME,
        level=config.file_level.name,
    )


def enable_file_logging(
    filename: str,
    logger_name: str = LOGGER_NAME,
    level: int | str | None = None,
    *,
    json: bool = True,
):
    """
    Add a FileHandler. If `level` is None, it inherits the logger's level.
    Set json=False to use the plain text formatter.
    """
    logger = logging.getLogger(logger_name)
    file_handler = FileHandler(filename)

    if level is None:
        # Let the logger's level govern emission from this handler
        file_handler.setLevel(logging.NOTSET)
    elif logger.level > _parse_level(level):
        logger.setLevel(_parse_level(level))
        file_handler.setLevel(_parse_level(level))
    else:
        file_handler.setLevel(_parse_level(level))

    if json:
        # ISO-ish date for JSON logs; keep keys consistent with LOGGING_FORMAT fields
        formatter = JsonFormatter(LOGGING_FORMAT, datefmt="%Y-%m-%dT%H:%M:%S")
    else:
        formatter = logging.Formatter(LOGGING_FORMAT, datefmt="%d-%m-%Y %I:%M:%S")

    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    # prevent double emission to ancestor loggers
    logger.propagate = False
    return file_handler


def set_log_file(filename: str, level: int, logger_name=LOGGER_NAME):
    logger = logging.getLogger(LOGGER_NAME)
    # Remove existing FileHandlers
    for h in list(logger.handlers):
        if isinstance(h, FileHandler):
            logger.removeHandler(h)
            h.close()
    enable_file_logging(filename, logger_name, level)


def set_log_level(level: int | str, logger_name: str = LOGGER_NAME):
    """
    Update the logger and all attached handlers to the given level.
    """
    lvl = _parse_level(level)
    logger = logging.getLogger(logger_name)
    logger.setLevel(lvl)
    for h in logger.handlers:
        h.setLevel(lvl)


def _parse_level(level: int | str) -> int:
    """Accept logging.DEBUG or 'DEBUG' (case-insensitive) and return an int level."""
    if isinstance(level, int):
        return level
    if isinstance(level, str):
        name = level.strip().upper()
        if name.isdigit():
            return int(name)
        if hasattr(logging, name):
            return getattr(logging, name)
    raise ValueError(f"Invalid log level: {level!r}")
