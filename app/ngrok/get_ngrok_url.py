import asyncio
import logging

import httpx

logger = logging.getLogger(__name__)


async def get_ngrok_public_url(
    ngrok_api_url: str = "http://ngrok:4040",
    retries: int = 20,
    delay: float = 0.5,
) -> str | None:
    url = f"{ngrok_api_url}/api/endpoints"

    for attempt in range(1, retries + 1):
        try:
            async with httpx.AsyncClient(timeout=3) as client:
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()

            endpoints: list[dict[str, str]] = data.get("endpoints", [])

            if endpoints:
                return endpoints[0]["url"]
            return None

        except Exception as error:
            logger.debug(
                "Ngrok public URL is not ready yet. Attempt %s/%s. Error: %s",
                attempt,
                retries,
                error,
            )

        await asyncio.sleep(delay)

    raise RuntimeError("Could not get ngrok public URL")
