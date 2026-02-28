本文档先解析每个 Python 模块的核心对象，再给出对应的伪代码。

**服务端目录**

```
server_launch.py  # 服务端启动
config.py         # 服务端配置加载
logging.py        # 日志模块
exception.py      # 异常类
/api
    app.py
    admin_endpoint.py   # 管理端 API Endpoint
    user_endpoint.py    # 用户端 API Endpoint
/data
    orm.py        # SQLAlchemy 数据库表对应的 ORM 类
    model.py      # 定义数据结构
    operation.py  # 数据库操作 API
    cache.py      # 数据库缓存支持
    utils.py
/service
    cv_extraction.py  # 简历提取工作流
    /interview        # 面试支持
        interview.py
        /utils
            agent.py  # 面试智能体
            audio.py  # 语音工具
            judge.py  # 回答评价工作流
```

**客户端目录 (管理端 CLI 工具)**
```
pyproject.toml  # 配置文件
/interview_manager
    cli.py       # CLI 工具入口
    commands.py  # 命令实现
```

**客户端目录 (用户端)**
```
user_app.py  # 用户端 Gradio App
/cache       # 本地数据缓存
```

**模块介绍**

- `api`: 将整个服务端封装成一个 FastAPI App
- `service`: 实现核心服务。
- `service.cv_extraction`: 简历提取工作流。
- `service.interview`: 面试支持。






