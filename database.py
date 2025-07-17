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

    def __set_column_value(self, server_id: str, col: Column, val: str) -> None:
        query = f"""
            INSERT INTO {self.__table_name} ({Column.id}, {col})
            VALUES (?, ?)
            ON CONFLICT({Column.id}) DO UPDATE SET
                {col} = excluded.{col}
        """  # noqa: S608
        self.__conn.cursor().execute(query, (server_id, val))
        self.__conn.commit()

    def __get_column_value(self, server_id: str, col: Column) -> str | None:
        query = f"SELECT {col} from {self.__table_name} where {Column.id} = ?"  # noqa: S608
        cursor = self.__conn.cursor()
        cursor.execute(query, (server_id,))

        result = cursor.fetchone()
        return result[0] if result else None

    def set_x_api_key(self, server_id: str, x_api_key: str) -> None:
        self.__set_column_value(server_id, Column.x_api_key, x_api_key)

    def set_trigger_emoji(self, server_id: str, trigger_emoji: str) -> None:
        self.__set_column_value(server_id, Column.trigger_emoji, trigger_emoji)

    def set_emoji_reaction_threshhold(self, server_id: str, threshhold: int) -> None:
        self.__set_column_value(
            server_id,
            Column.emoji_reaction_threshhold,
            str(threshhold),
        )

    def set_reaction_observing_timeout_secs(
        self,
        server_id: str,
        timeout_secs: int,
    ) -> None:
        self.__set_column_value(
            server_id,
            Column.reaction_observing_timeout_secs,
            str(timeout_secs),
        )

    def get_trigger_emoji(self, server_id: str) -> str | None:
        return self.__get_column_value(server_id, Column.trigger_emoji)

    def get_emoji_reaction_threshhold(self, server_id: str) -> int | None:
        maybe_threshhold = self.__get_column_value(
            server_id,
            Column.emoji_reaction_threshhold,
        )
        return int(maybe_threshhold) if maybe_threshhold else None

    def get_reaction_observing_timeout_secs(self, server_id: str) -> int:
        maybe_timeout = self.__get_column_value(
            server_id,
            Column.reaction_observing_timeout_secs,
        )

        if maybe_timeout is None:
            e = f"Expected non-null value for column '{Column.reaction_observing_timeout_secs}'"
            raise ValueError(e)

        return int(maybe_timeout)
