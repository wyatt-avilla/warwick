import atexit
import logging
import sqlite3
from pathlib import Path


class DatabaseInterface:
    def __init__(self, database_path: Path) -> None:
        self.logger = logging.getLogger(__name__)
        self.db_path = database_path
        self.conn = self.__db_conn_init(database_path)

        atexit.register(self.__close)

    def __del__(self) -> None:
        self.__close()

    def __close(self) -> None:
        self.conn.close()

    def __db_conn_init(self, database_path: Path) -> sqlite3.Connection:
        if not database_path.exists():
            self.logger.warning(
                "Requested database '%s' doesn't exist, creating...",
                database_path,
            )

        return sqlite3.connect(self.db_path)

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
