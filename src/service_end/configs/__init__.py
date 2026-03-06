from ..exception import ServiceInitException
import os
import yaml
from pathlib import Path


try:
    # 一般配置
    with open(Path(__file__).parent/"config.yaml", encoding="utf-8") as f:
        __config = yaml.load(f, Loader=yaml.FullLoader)
    
    INTERVAL = __config["log"]["interval"]
    TIME_BACKUP_COUNT = __config["log"]["time_backupCount"]
    MAX_MB = __config["log"]["maxMB"]
    FILE_BACKUP_COUNT = __config["log"]["file_backupCount"]
    
    APP_KWARGS = __config["run"]["app"]
    FASTAPI_KWARGS = __config["run"]["fastapi"]
    CACHE_CONFIG = __config["cache"]
    DATA_CONFIG = __config["data"]
    
    assert (
        isinstance(INTERVAL, int) and 
        isinstance(TIME_BACKUP_COUNT, int) and 
        isinstance(FILE_BACKUP_COUNT, int) and 
        isinstance(MAX_MB, int)
    )

    # 日志路径, 日志初始化
    with open(Path(__file__).parent/"log_path.yaml", encoding="utf-8") as f:
        __log_path = yaml.load(f, Loader=yaml.FullLoader)

    LOG_ROOT = os.path.join(os.getcwd(), __log_path["log_root"])
    COMMON_LOG = os.path.join(LOG_ROOT, __log_path["common_log"])
    ERROR_LOG = os.path.join(LOG_ROOT, __log_path["error_log"])

    if __config["log"]["clear_when_start"]:
        if os.path.exists(LOG_ROOT):
            import shutil
            shutil.rmtree(LOG_ROOT)
    if not os.path.exists(LOG_ROOT):
        os.mkdir(LOG_ROOT)

    # 面试配置
    


except Exception as e:
    raise ServiceInitException(source_class=None, message=str(e))