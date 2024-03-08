from loguru import logger

# Define the log format including {log_id}

# Add a handler to write logs to file
logger.add(
    "logs/app.log",
    level="DEBUG",
    rotation="10 MB",
    format="{time:DD-MM-YYYY hh:mm:ss A} - {level} - {message}",
)
