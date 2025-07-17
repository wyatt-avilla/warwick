from __future__ import annotations

import atexit
import logging
import sqlite3
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path


class Column(str, Enum):
    id = "id"
    x_api_key = "x_api_key"
    trigger_emoji = "trigger_emoji"
    emoji_reaction_threshhold = "emoji_reaction_threshhold"
    reaction_observing_timeout_secs = "reaction_observing_timeout_secs"

    def __str__(self) -> str:
        return self.value


class DatabaseInterface:
    def __init__(self, database_path: Path) -> None:
        self.db_path = database_path

        self.__logger = logging.getLogger(__name__)
        self.__conn = self.__db_conn_init(database_path)
        self.__table_name = "server_configs"

        self.__create_table_if_needed()

        atexit.register(self.__close)

    def __del__(self) -> None:
        self.__close()

    def __close(self) -> None:
        self.__conn.close()

    def __db_conn_init(self, database_path: Path) -> sqlite3.Connection:
        if not database_path.exists():
            self.__logger.warning(
                "Requested database '%s' doesn't exist, creating...",
                database_path,
            )

        return sqlite3.connect(self.db_path)

    def __create_table_if_needed(self) -> None:
        table_creation_rule = f"""
        CREATE TABLE IF NOT EXISTS {self.__table_name} (
            {Column.id} TEXT PRIMARY KEY,
            {Column.x_api_key} TEXT,
            {Column.trigger_emoji} TEXT,
            {Column.emoji_reaction_threshhold} INTEGER,
            {Column.reaction_observing_timeout_secs} INTEGER DEFAULT {60 * 5}
        )
        """
        self.__conn.cursor().execute(table_creation_rule)
        self.__conn.commit()

    def set_x_api_key(self, server_id: str, x_api_key: str) -> None:
        raise NotImplementedError

    def set_trigger_emoji(self, server_id: str, trigger_emoji: str) -> None:
        raise NotImplementedError

    def set_emoji_reaction_threshhold(self, server_id: str, threshhold: int) -> None:
        raise NotImplementedError

    def set_reaction_observing_timeout_secs(
        self,
        server_id: str,
        timeout_secs: int,
    ) -> None:
        raise NotImplementedError

    def get_trigger_emoji(self, server_id: str) -> str | None:
        raise NotImplementedError

    def get_emoji_reaction_threshhold(self, server_id: str) -> int | None:
        raise NotImplementedError

    def get_reaction_observing_timeout_secs(self, server_id: str) -> int:
        raise NotImplementedError
