# 1. 服务端创建环境

```bash
> conda create env-name python=3.11.14
> conda activate env-name
> pip install -r requirements.txt
```

# 2. 服务端

```
service_end
    ├── launch.py            # 服务端启动入口
    ├── exception.py         # 服务端异常
    ├── configs              # yaml 配置文件
    │   ├── app.yaml         # app 启动
    │   ├── db_cache.yaml    # 数据库缓存
    │   └── table_init.yaml  # 数据库创建
    ├── data                 # 数据模型、数据库模块
    │   ├── __init__.py      # 数据库初始化，DataBaseManager
    │   ├── utils.py
    │   ├── cache.py         # 数据库读取缓存
    │   ├── model.py         # Pydantic 数据模型
    │   ├── orm.py           # SQLAlchemy ORM 类
    │   └── operation.py     # 数据操作 API
    └── service              # 服务
        ├── parse_cv.py      # 简历结构化提取 (待开发)
        ├── question_gen.py  # 面试问题生成 (待开发)
        └── interview        # 面试支持模块 (待开发)
```

# 3. 开发计划

- 服务端日志与异常处理框架开发
- 简历结构化提取 & 面试问题生成
- 管理端封装
- 用户端 + 面试支持模块协同开发