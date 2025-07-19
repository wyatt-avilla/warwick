from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import TYPE_CHECKING

from tweepy import API, OAuth1UserHandler
from tweepy.asynchronous import AsyncClient

import media_streaming

if TYPE_CHECKING:
    from type_aliases import URL
from typing import TYPE_CHECKING


@dataclass
class AuthenticationBundle:
    bearer_token: str
    api_key: str
    api_key_secret: str
    access_token: str
    access_token_secret: str


class Account:
    def __init__(self, auth: AuthenticationBundle) -> None:
        self.auth = auth
        self.client = AsyncClient(
            bearer_token=auth.bearer_token,
            consumer_key=auth.api_key,
            consumer_secret=auth.api_key_secret,
            access_token=auth.access_token,
            access_token_secret=auth.access_token_secret,
        )

    async def __post(
        self,
        *,
        text: str | None = None,
        media_ids: list[str] | None = None,
    ) -> URL:
        response = await self.client.create_tweet(text=text, media_ids=media_ids)
        post_id = response.data["id"]

        return await self.__post_url_from(post_id)

    async def __get_username(self) -> str:
        return str((await self.client.get_me()).data.username)

    def __get_oauth_user_handler(self) -> OAuth1UserHandler:
        return OAuth1UserHandler(
            self.auth.api_key,
            self.auth.api_key_secret,
            self.auth.access_token,
            self.auth.access_token_secret,
        )

    async def __post_url_from(self, post_id: str) -> URL:
        username = await self.__get_username()

        return f"https://x.com/{username}/status/{post_id}"

    async def create_text_post(self, text: str) -> URL:
        return await self.__post(text=text)

    async def create_post_with_media(
        self,
        *,
        text: str | None,
        media_links: tuple[URL]
        | tuple[URL, URL]
        | tuple[URL, URL, URL]
        | tuple[URL, URL, URL, URL],
    ) -> URL:
        api = API(auth=self.__get_oauth_user_handler())

        async def process_media_link(media_link: URL) -> str:
            mem_file = await media_streaming.bytesio_from_url(media_link)
            media = api.chunked_upload(
                media_link.split("/")[-1],
                file=mem_file,
                wait_for_async_finalize=True,
            )
            return str(media.media_id_string)

        media_ids = await asyncio.gather(
            *[process_media_link(media_link) for media_link in media_links],
        )

        return await self.__post(text=text, media_ids=media_ids)
