from ..exception import DBCacheError, ServiceInitException
import time
import inspect
from collections import OrderedDict
from typing import Any, Callable
from enum import Enum
from functools import wraps


class KeyType(Enum):
    """缓存键类型枚举"""

    DOMAIN_SUBDOMAIN = "DOMAIN_SUBDOMAIN"
    CV_TITLE = "CV_TITLE"
    QUESTION_BANK = "QUESTION_BANK"
    ALL_DOMAIN_NAME = "ALL_DOMAIN_NAME"
    ALL_JOB = "ALL_JOB"
    ALL_CV_TITLE = "ALL_CV_TITLE"
    ALL_LLM = "ALL_LLM"
    ALL_INTERVIEWER = "ALL_INTERVIEWER"


class KeyFactory:
    """
    规范缓存键工厂
    
    添加新缓存：
    1. 在 `KeyTpye` 加上键类型
    2. 在 `KeyFactory` 下方添加对应的 _get 方法
    3. 在 router 中注册 _get 方法
    """

    @classmethod
    def get(cls, key_type: KeyType, **kwargs) -> str:
        """生产缓存键。键内参数通过 `kwargs` 传入"""
        getter = cls._method_router(key_type=key_type)
        arg_name_set = set(inspect.signature(getter).parameters.keys())  # getter 参数名称集合
        if arg_name_set <= set(kwargs.keys()):
            return getter(
                **{k: kwargs[k] for k in arg_name_set}
            )
        else:
            raise DBCacheError(f"cache key building arg missing: {arg_name_set.difference(set(kwargs.keys()))}")

    @classmethod
    def _method_router(cls, key_type: KeyType) -> Callable[..., str]:
        if key_type == KeyType.DOMAIN_SUBDOMAIN:
            return cls.__get_domain_subdomain
        elif key_type == KeyType.CV_TITLE:
            return cls.__get_cv_title
        elif key_type == KeyType.QUESTION_BANK:
            return cls.__get_question_bank
        elif key_type == KeyType.ALL_DOMAIN_NAME:
            return cls.__get_all_domain_name
        elif key_type == KeyType.ALL_JOB:
            return cls.__get_all_job
        elif key_type == KeyType.ALL_CV_TITLE:
            return cls.__get_all_cv_title
        elif key_type == KeyType.ALL_LLM:
            return cls.__get_all_llm
        elif key_type == KeyType.ALL_INTERVIEWER:
            return cls.__get_all_interviewer
        else:
            raise DBCacheError(f"invalid key type: {key_type}")

    @classmethod
    def __get_domain_subdomain(cls, domain_name: str, sub_domain_name: str) -> str:
        return f"{domain_name}-{sub_domain_name}"

    @classmethod
    def __get_cv_title(cls, title: str) -> str:
        return f"CV-{title}"

    @classmethod
    def __get_question_bank(cls, domain_name: str) -> str:
        return f"QUESTION_BANK_{domain_name}"

    @classmethod
    def __get_all_domain_name(cls) -> str:
        return "ALL_DOMAIN_NAME"

    @classmethod
    def __get_all_job(cls) -> str:
        return "ALL_JOB"

    @classmethod
    def __get_all_cv_title(cls) -> str:
        return "ALL_CV_TITLE"

    @classmethod
    def __get_all_llm(cls) -> str:
        return "ALL_LLM"

    @classmethod
    def __get_all_interviewer(cls) -> str:
        return "ALL_INTERVIEWER"


class DBCache:
    """
    数据库查询缓存 (FIFO, 键值对数据)
    
    缓存对象
    ```
    | key | value | 关联 table |
    | --- | --- | --- |
    | {domain_name}-{sub_domain_name} | (domain_id, sub_domain_id) | Domain |
    | CV-{title} | CVModel 对象 | CV |
    | QUESTION_BANK_{domain_name} | DomainQuestionBank 对象 | Domain, Question |
    | ALL_JOB | JobModel 的列表 | Job |
    | ALL_CV_TITLE | 所有 CV 的 title 的列表 | CV |
    | ALL_LLM | 所有 LLMCard 的列表 | LLM |
    | ALL_INTERVIEWER | 所有 Interviewer 的列表 | Interviewer |
    ```

    Attributes:
        ttl (float): 缓存存活时间, 单位 sec
        size (int): 缓存条数
        cache (OrderedDict): 缓存数据。key: 缓存索引, value: (创建时间戳, 数据对象)
    """

    def __init__(self, size: int, ttl: float):
        assert ttl > 0
        self.ttl = ttl
        self.size = max(size, 1)
        self.cache: OrderedDict[str, tuple[float, Any]] = OrderedDict()

    def __check_alive(self, create_timestamp: float) -> bool:
        """缓存有效性检查"""
        return time.time() - create_timestamp < self.ttl
    
    def __check_alive_and_remove(self):
        """检查全部缓存数据有效性, 移除无效数据"""
        keys = list(self.cache.keys())
        for key in keys:
            if not self.__check_alive(self.cache[key][0]):
                self.cache.pop(key)
    
    def get(self, key: str,) -> Any | None:
        """
        尝试获取一组缓存。key 不存在时返回 `None`
        """
        value = self.cache.get(key)
        if value is not None:
            create_timestamp, data = value
            if self.__check_alive(create_timestamp):
                return data
            else:
                self.cache.pop(key)
        return None  # 缓存对象本身就不存在，或被 pop 掉了

    def update(self, key: str, value: Any, check_alive: bool = True) -> None:
        """创建/更新一个缓存"""
        if check_alive:
            self.__check_alive_and_remove()
        if len(self.cache) >= self.size:
            self.cache.popitem(last=False)  # FIFO
        self.cache[key] = (time.time(), value,)

    def batch_update(self, data: dict) -> None:
        """创建/更新一批缓存"""
        self.__check_alive_and_remove()
        for k, v in data.items():
            self.update(key=k, value=v, check_alive=False)

    def pop(self, key: str) -> None:
        """删除一个缓存对象"""
        if key in self.cache:
            self.cache.pop(key)


try:
    from ..configs import CACHE_CONFIG
    GLOBAL_CACHE = DBCache(size=CACHE_CONFIG["cache_size"], ttl=CACHE_CONFIG["cache_ttl"])
except KeyError as e:
    raise ServiceInitException(source_class=None, message=f"config key missing: {e}")


def with_cache_async(key_type: KeyType):
    """
    函数返回结果缓存装饰器。
    
    当缓存中不存在指定数据时，调用被装饰函数创建对象后返回，否则直接返回缓存数据。
    注意：缓存键参数必须以关键字形式从被装饰函数传入。
    """
    def decorator(fn):
        @wraps(fn)
        async def wrapped_fn(*args, **kwargs):
            KEY = KeyFactory.get(key_type=key_type, **kwargs)
            cache_data = GLOBAL_CACHE.get(KEY)
            if cache_data is not None:
                data = cache_data
            else:
                data = await fn(*args, **kwargs)
                GLOBAL_CACHE.update(key=KEY, value=data)
            return data
        return wrapped_fn
    return decorator

