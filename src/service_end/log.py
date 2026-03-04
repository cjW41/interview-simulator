from .configs import ERROR_LOG, COMMON_LOG, INTERVAL, TIME_BACKUP_COUNT, FILE_BACKUP_COUNT, MAX_MB
import logging
import queue
from logging.handlers import TimedRotatingFileHandler, RotatingFileHandler, QueueHandler, QueueListener

DETAIL_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
ROOT_LEVEL = logging.INFO

_queue_listener = None

def setup_log():
    global _queue_listener
    
    # 根日志记录器
    logger = logging.getLogger()
    logger.setLevel(ROOT_LEVEL)
    
    # 清除其它 handler
    logger.handlers.clear()

    # 创建日志队列（无限大小）
    log_queue = queue.Queue(-1)

    # 一般详细日志
    common_handler = TimedRotatingFileHandler(
        filename=COMMON_LOG,
        when="midnight",  # 日志轮转日期
        interval=INTERVAL,
        backupCount=TIME_BACKUP_COUNT,
        encoding="utf-8"
    )
    common_handler.setLevel(ROOT_LEVEL)
    common_handler.setFormatter(logging.Formatter(DETAIL_FORMAT))

    # 错误级以上单独记录日志
    error_handler = RotatingFileHandler(
        filename=ERROR_LOG,
        maxBytes=MAX_MB * 1024 * 1024,
        backupCount=FILE_BACKUP_COUNT,
        encoding="utf-8"
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(logging.Formatter(DETAIL_FORMAT))

    # 创建 QueueListener，在后台线程中处理日志
    _queue_listener = QueueListener(
        log_queue,
        common_handler,
        error_handler,
        respect_handler_level=True
    )
    _queue_listener.start()

    # 根日志记录器只添加 QueueHandler
    logger.addHandler(QueueHandler(log_queue))

    # 过滤 uvicorn 和 sqlalchemy 的日志到 WARNING 级及以上
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


def shutdown_log():
    global _queue_listener
    if _queue_listener is not None:
        _queue_listener.stop()
        _queue_listener = None
