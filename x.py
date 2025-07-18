from dataclasses import dataclass

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
        self.client = AsyncClient(
            bearer_token=auth.bearer_token,
            consumer_key=auth.api_key,
            consumer_secret=auth.api_key_secret,
            access_token=auth.access_token,
            access_token_secret=auth.access_token_secret,
        )

    async def get_username(self) -> str:
        return str((await self.client.get_me()).data.username)

    async def post_url_from(self, post_id: str) -> URL:
        username = await self.get_username()

        return f"https://x.com/{username}/status/{post_id}"

    async def create_text_post(self, text: str) -> URL:
        response = await self.client.create_tweet(text=text)

        post_id = response.data["id"]

        return await self.post_url_from(post_id)
