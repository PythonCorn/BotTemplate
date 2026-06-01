from httpx import AsyncClient


class HttpxService:
    def __init__(self):
        self.session = AsyncClient()

    async def close(self):
        await self.session.aclose()