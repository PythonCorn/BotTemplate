from fastapi import FastAPI

from app.core.lifespan import lifespan


def create_app() -> FastAPI:
    app = FastAPI(
        title="Bot Template",
        lifespan=lifespan,
    )

    # api routes подключим следующим шагом

    return app
