from data import db_init
from api import create_app
from api.dependency import DependencyModel
import uvicorn


# 加载 数据库/app
I, G, U, D = db_init()  # TODO 从配置文件加载
dependency = DependencyModel(insert_operator=I, get_operator=G, update_operator=U, delete_operator=D)
app = create_app(dependency=dependency)


if __name__ == "__main__":
    uvicorn.run(app=app)


