class ServiceInitException(Exception):
    """服务端启动异常"""
    def __init__(self, source_class: str | None, message: str):
        super().__init__()
        self.source_class = source_class
        self.message = message

    def __str__(self) -> str:
        return f"source: {self.source_class}, message: {self.message}"


class ServiceEndExceptionBase(Exception):
    """
    服务端异常基类。
    开发中不可直接 raise 这一异常。
    """
    pass


class DatabaseException(ServiceEndExceptionBase):
    """service_end.data 异常基类"""
    def __init__(self, table: str):
        super().__init__()
        self.table = table

    def __str__(self) -> str:
        return f"table: {self.table}"


class ServiceException(ServiceEndExceptionBase):
    """service_end.service 模块内异常基类"""
    pass


class UploadError(ServiceEndExceptionBase):
    """用户上传文件异常"""
    def __init__(self, message: str, file_name: str):
        super().__init__()
        self.file_name = file_name
        self.message = message

    def __str__(self) -> str:
        return f"{self.message}. file name: {self.file_name}"

