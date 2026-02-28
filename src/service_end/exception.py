import time


class ServiceException(Exception):
    """服务端异常基类"""
    def __init__(self):
        self.timestamp = time.time()


class ServiceInitException(ServiceException):
    """服务端启动异常"""
    def __init__(self, source_class: str | None, message: str):
        super().__init__()
        self.source_class = source_class
        self.message = message

    def __str__(self) -> str:
        return f"source: {self.source_class}, message: {self.message}"


class DatabaseException(ServiceException):
    """数据库异常基类"""
    def __init__(self, *messages: str):
        super().__init__()
        self.messages = messages
    
    def __str__(self) -> str:
        return " ".join(self.messages)

class TragetRecordNotFound(DatabaseException):
    """调用 DQL 语句时未找到目标记录"""
    def __init__(self, table: str, filter_condition: str):
        super().__init__()
        self.table = table
        self.filter_condition = filter_condition

    def __str__(self) -> str:
        return f"table: {self.table}, condition: {self.filter_condition}"


class InsertError(DatabaseException):
    """调用 insert 插入数据时出现异常，转化自 `SQLAlchemyError`"""
    def __init__(self, source_class: str, table: str, data: list):
        super().__init__()
        self.source_class = source_class
        self.table = table
        self.data = data
        
    def __str__(self) -> str:
        return f"source: {self.source_class}, table: {self.table}, first_data: {self.data[0]}"


class UpdateError(DatabaseException):
    """调用 update 修改数据时出现异常，转化自 `SQLAlchemyError`"""
    def __init__(self, source_class: str, table: str, filter_condition: str, value: dict):
        super().__init__()
        self.source_class = source_class
        self.table = table
        self.filter_condition = filter_condition
        self.value = value
    
    def __str__(self,) -> str:
        return f"source: {self.source_class}, table: {self.table}, filter: {self.filter_condition}, value: {self.value}"







