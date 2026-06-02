from fastapi import FastAPI

from app.api import webhook
from app.core.lifespan import lifespan

app = FastAPI(lifespan=lifespan)

app.include_router(router=webhook.router)
