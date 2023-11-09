import logging
from os import getenv

# Create a logger
logger = logging.getLogger("NodeWatch")
logger.setLevel(logging.DEBUG)

# Create a file handler
file_handler = logging.FileHandler(getenv("LOG_FILE_NAME"))
file_handler.setLevel(logging.DEBUG)

# Create a console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

# Create a custom log message format with color
log_format = "%(asctime)s - %(levelname)s - %(message)s"
console_formatter = logging.Formatter(log_format)

# Set the formatter for the console handler
console_handler.setFormatter(console_formatter)

# Add the handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)


def get_logger():
    return logger
