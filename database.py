import atexit
import sqlite3
from pathlib import Path


class DatabaseInterface:
    def __init__(self, database_path: Path) -> None:
        self.db_path = database_path
        self.conn: sqlite3.Connection = sqlite3.connect(self.db_path)

        atexit.register(self.close)

    def __del__(self) -> None:
        self.close()

    def close(self) -> None:
        self.conn.close()

    def set_x_api_key(self, server_id: str, x_api_key: str) -> None:
        raise NotImplementedError

    def set_trigger_emoji(self, server_id: str, trigger_emoji: str) -> None:
        raise NotImplementedError

    def set_emoji_reaction_threshhold(self, server_id: str, threshhold: int) -> None:
        raise NotImplementedError

    def get_trigger_emoji(self, server_id: str) -> str:
        raise NotImplementedError

    def get_emoji_reaction_threshhold(self, server_id: str) -> int:
        raise NotImplementedError
