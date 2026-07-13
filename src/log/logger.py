"""
biz_log 业务日志：
    控制台输出、独立日志目录输出文件，不带额外格式

common_log 普通日志：
    控制台输出、日志文件输出，标注格式
"""
import logging, os
from logging.handlers import TimedRotatingFileHandler
from config.config import settings


logger_name = settings.LOGGER_CONFIG.get("logger-name")
file_name = settings.LOGGER_CONFIG.get("file-name")
file_dir = settings.LOGGER_CONFIG.get("file-path")
try:
    os.makedirs(file_dir, exist_ok=True)
except PermissionError:
    file_dir = os.path.join(os.getcwd(), "logs", settings.SERVICE_NAME)
    os.makedirs(file_dir, exist_ok=True)

file_path = os.path.join(file_dir, file_name)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler = TimedRotatingFileHandler(
    file_path,
    when='D',
    interval=1,
    backupCount=30
)
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.INFO)


httpx_logger = logging.getLogger("httpx")
httpx_logger.setLevel(logging.INFO)
httpx_logger_handler = logging.StreamHandler()
httpx_logger_handler.setFormatter(formatter)
httpx_logger.addHandler(httpx_logger_handler)
httpx_logger.addHandler(file_handler)


def __get_common_logger():
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
    return logger

logger = __get_common_logger()
