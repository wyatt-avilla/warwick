from dataclasses import dataclass

from tweepy.asynchronous import AsyncClient


@dataclass
class AuthenticationBundle:
    bearer_token: str
    api_key: str
    api_key_secret: str
    access_token: str
    access_token_secret: str


async def create_text_post(auth: AuthenticationBundle, text: str) -> None:
    client = AsyncClient(
        bearer_token=auth.bearer_token,
        consumer_key=auth.api_key,
        consumer_secret=auth.api_key_secret,
        access_token=auth.access_token,
        access_token_secret=auth.access_token_secret,
    )

    await client.create_tweet(text=text)
