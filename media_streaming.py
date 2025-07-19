from io import BytesIO

import aiohttp

from type_aliases import URL


async def bytesio_from_url(url: URL) -> BytesIO:
    async with aiohttp.ClientSession() as session, session.get(url) as response:
        bytesio = BytesIO()

        async for chunk in response.content.iter_any():
            bytesio.write(chunk)
        bytesio.seek(0)

        return bytesio
