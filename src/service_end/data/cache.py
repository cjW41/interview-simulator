import time
from collections import OrderedDict
from typing import Any


class DBCache:
    """
    数据库查询缓存 (FIFO, 键值对数据)
    
    缓存对象
    ```
    key | value | 关联 table
    {domain_name}-{sub_domain_name} | (domain_id, sub_domain_id) | Domain
    CV-{title} | CVModel 对象 | CV
    ALL_JOB | JobModel 的列表 | Job
    ALL_CV_TITLE | 所有 CV 的 title 的列表 | CV
    ALL_LLM | 所有 LLMCard 的列表 | LLM
    ALL_INTERVIEWER | 所有 Interviewer 的列表 | Interviewer
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

    def _check_alive(self, create_timestamp: float) -> bool:
        """缓存有效性检查"""
        return time.time() - create_timestamp < self.ttl
    
    def _check_alive_and_remove(self):
        """检查全部缓存数据有效性, 移除无效数据"""
        keys = list(self.cache.keys())
        for key in keys:
            if not self._check_alive(self.cache[key][0]):
                self.cache.pop(key)
    
    def get(self, key: str,) -> Any | None:
        """
        尝试获取一组缓存。key 不存在时返回 `None`
        """
        value = self.cache.get(key)
        if value is not None:
            create_timestamp, data = value
            if self._check_alive(create_timestamp):
                return data
            else:
                self.cache.pop(key)
        return None  # 缓存对象本身就不存在，或被 pop 掉了

    def update(self, key: str, value: Any, check_alive: bool = True) -> None:
        """创建/更新一组缓存"""
        if check_alive:
            self._check_alive_and_remove()
        if len(self.cache) >= self.size:
            self.cache.popitem(last=False)  # FIFO
        self.cache[key] = (time.time(), value,)

    def batch_update(self, data: dict) -> None:
        """创建/更新一批缓存"""
        self._check_alive_and_remove()
        for k, v in data.items():
            self.update(key=k, value=v, check_alive=False)

    def pop(self, key: str) -> None:
        """删除一个缓存对象"""
        if key in self.cache:
            self.cache.pop(key)


