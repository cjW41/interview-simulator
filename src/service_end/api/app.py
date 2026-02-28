# fastapi app
from .dependency import AppDependency, FastAPIwithDI
from .endpoint.admin_endpoint import router as admin_router
from .endpoint.user_endpoint import router as user_router


def create_app(dependency: AppDependency) -> FastAPIwithDI:
    app = FastAPIwithDI(title="Interview Simulator Service-End API")
    app.include_router(admin_router)
    app.include_router(user_router)
    app.inject_my_dependency(dependency=dependency)
    return app



