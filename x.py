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


async def create_text_post(auth: AuthenticationBundle, text: str) -> URL:
    client = AsyncClient(
        bearer_token=auth.bearer_token,
        consumer_key=auth.api_key,
        consumer_secret=auth.api_key_secret,
        access_token=auth.access_token,
        access_token_secret=auth.access_token_secret,
    )

    response = await client.create_tweet(text=text)

    username = (await client.get_me()).data.username
    post_id = response.data["id"]

    return f"https://x.com/{username}/status/{post_id}"
