from app.httpx_service import HttpxService

from typing import Protocol


class ClosableService(Protocol):
    async def close(self) -> None:
        ...


class Container:
    def __init__(self, *services: HttpxService, **kwargs):
        self.services = services
        self.kwargs = kwargs

    async def shutdown(self):
        for service in self.services:
            await service.close()

