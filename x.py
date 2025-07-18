from __future__ import annotations

from dataclasses import dataclass

from tweepy import API, OAuth1UserHandler
from tweepy.asynchronous import AsyncClient

type URL = str


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
        media_ids: str | None = None,
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
