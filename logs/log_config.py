from loguru import logger
# Define the log format including {log_id}
log_format = "{time:DD-MM-YYYY HH:mm:ss} - {level} - {message}"

# Add a handler to write logs to file
logger.add("logs/app.log", level="INFO", rotation="10 MB", format=log_format)
