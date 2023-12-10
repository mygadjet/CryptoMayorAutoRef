import logging
import colorlog

def setup_logger(name='project', log_file='project.log', level=logging.DEBUG):
    """Return a logger with a default ColoredFormatter."""
    formatter = colorlog.ColoredFormatter(
        "%(log_color)s%(asctime)s | %(name)s | %(levelname)-8s%(reset)s| "
        "%(blue)s[%(funcName)s]: %(message)s",
        datefmt='%Y-%m-%d %H:%M:%S',
        reset=True,
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        },
        secondary_log_colors={},
        style='%'
    )

    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)-8s [%(funcName)s]: %(message)s",
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    logger = logging.getLogger(name)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    logger.setLevel(level)

    return logger