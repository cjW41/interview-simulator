# 服务端异常类

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


class IntegrityDataError(DatabaseException):
    """DB-API `IntegrityError` + `DataError`"""
    def __init__(self, source_class: str, table: str, filter_condition: str):
        super().__init__(table)
        self.source_class = source_class
        self.filter_condition=filter_condition

    def __str__(self) -> str:
        return f"source: {self.source_class}, table: {self.table}, filter: {self.filter_condition}"


class TargetedRecordNotFound(DatabaseException):
    """指定记录未找到"""
    def __init__(self, table: str, not_found_filter_condition: str):
        super().__init__(table)
        self.filter_condition = not_found_filter_condition

    def __str__(self) -> str:
        return f"Targeted Record Not Found: (table: {self.table}, not_found_filter: {self.filter_condition})"

class QueryError(DatabaseException):
    """调用 DQL 语句时未找到目标记录"""
    def __init__(self, source_class: str, table: str, filter_condition: str):
        super().__init__(table)
        self.source_class = source_class

        self.filter_condition=filter_condition

    def __str__(self) -> str:
        return f"Query Error: (source: {self.source_class}, table: {self.table}, filter: {self.filter_condition})"


class InsertError(DatabaseException):
    """调用 insert 插入数据时出现异常，转化自 `SQLAlchemyError`"""
    def __init__(self, source_class: str, table: str):
        super().__init__(table)
        self.source_class = source_class
    
    def __str__(self) -> str:
        return f"Insert Error: (source: {self.source_class}, table: {self.table})"  


class UpdateError(DatabaseException):
    """调用 update 修改数据时出现异常，转化自 `SQLAlchemyError`"""
    def __init__(self, source_class: str, table: str, filter_condition: str):
        super().__init__(table)

        self.source_class = source_class
        self.filter_condition=filter_condition
    
    def __str__(self) -> str:
        return f"Update Error: (source: {self.source_class}, table: {self.table})"
    

class DeleteError(DatabaseException):
    """调用 delete 删除数据时出现异常，转化自 `SQLAlchemyError`"""
    def __init__(self, source_class: str, table: str, filter_condition: str):
        super().__init__(table)
        self.source_class = source_class
        self.filter_condition=filter_condition

    def __str__(self) -> str:
        return f"Delete Error: (source: {self.source_class}, table: {self.table}, filter: {self.filter_condition})"


class UpdateEmpty(DatabaseException):
    """更新未匹配到任何数据"""
    def __init__(self, table: str, filter_condition: str):
        super().__init__(table)
        self.filter_condition = filter_condition
    
    def __str__(self) -> str:
        return f"No Data to Update: (table: {self.table}, filter: {self.filter_condition})"


class DBCacheError(ServiceEndExceptionBase):
    """DBCache 产生的异常"""
    def __init__(self, message: str):
        super().__init__()
        self.message = message
    
    def __str__(self) -> str:
        return self.message


class UploadError(ServiceEndExceptionBase):
    """用户上传文件异常"""
    def __init__(self, message: str, file_name: str):
        super().__init__()
        self.file_name = file_name
        self.message = message

    def __str__(self) -> str:
        return f"{self.message}. file name: {self.file_name}"


class ServiceException(ServiceEndExceptionBase):
    """service_end.service 模块内异常基类"""
    pass


class QuestionGenException(ServiceException):
    """题库生成异常"""
    pass
