from loguru import logger
import sys
import uuid
log_id = str(uuid.uuid4())

logger.add(
    "logs/app.log", level="INFO", rotation="10 MB", format="{time:YYYY-MM-DD HH:mm:ss} - {level} - {message}"
)
logger.add(sys.stdout, level="DEBUG")
