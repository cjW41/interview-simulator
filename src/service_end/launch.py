from data import db_init
from api import create_app, FastAPIDependency

import uvicorn

# 加载数据库
i_operator, g_operator, u_operator, d_operator = db_init()  # 从 yaml 传入

# 加载 app
app = create_app(
    FastAPIDependency(
        insert_operator=i_operator,
        get_operator=g_operator,
        update_operator=u_operator,
        delete_operator=d_operator
    )
)


if __name__ == "__main__":
    uvicorn.run(app=app)


