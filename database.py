from __future__ import annotations

import atexit
import logging
from enum import Enum
from typing import TYPE_CHECKING

import aiosqlite

import x

if TYPE_CHECKING:
    from pathlib import Path


class Column(str, Enum):
    id = "id"
    trigger_emoji = "trigger_emoji"
    emoji_reaction_threshhold = "emoji_reaction_threshhold"
    x_bearer_token = "x_bearer_token"
    x_api_key = "x_api_key"
    x_api_key_secret = "x_api_key_secret"
    x_access_token = "x_access_token"
    x_access_token_secret = "x_access_token_secret"

    def __str__(self) -> str:
        return self.value


class DatabaseInterface:
    db_path: Path
    __logger: logging.Logger
    __conn: aiosqlite.Connection
    __table_name: str

    @staticmethod
    async def new(database_path: Path) -> DatabaseInterface:
        db = DatabaseInterface()
        db.db_path = database_path
        db.__logger = logging.getLogger(__name__)
        db.__conn = await DatabaseInterface.__db_conn_init(database_path, db.__logger)
        db.__table_name = "server_configs"

        return db

    @staticmethod
    async def __db_conn_init(
        database_path: Path,
        logger: logging.Logger,
    ) -> aiosqlite.Connection:
        if not database_path.exists():
            logger.warning(
                "Requested database '%s' doesn't exist, creating...",
                database_path,
            )

        return await aiosqlite.connect(database_path)

    @staticmethod
    async def __create_table_if_needed(
        db_connection: aiosqlite.Connection,
        table_name: str,
    ) -> None:
        table_creation_rule = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            {Column.id} TEXT PRIMARY KEY,
            {Column.trigger_emoji} TEXT,
            {Column.emoji_reaction_threshhold} INTEGER,
            {Column.x_bearer_token} TEXT,
            {Column.x_api_key} TEXT,
            {Column.x_api_key_secret} TEXT,
            {Column.x_access_token} TEXT,
            {Column.x_access_token_secret} TEXT
        )
        """
        cursor = await db_connection.cursor()

        await cursor.execute(table_creation_rule)
        await db_connection.commit()

        await cursor.close()

    async def __set_column_value(self, server_id: str, col: Column, val: str) -> None:
        query = f"""
            INSERT INTO {self.__table_name} ({Column.id}, {col})
            VALUES (?, ?)
            ON CONFLICT({Column.id}) DO UPDATE SET
                {col} = excluded.{col}
        """  # noqa: S608
        cursor = await self.__conn.cursor()

        await cursor.execute(query, (server_id, val))
        await self.__conn.commit()

        await cursor.close()

    async def __get_column_value(self, server_id: str, col: Column) -> str | None:
        query = f"SELECT {col} from {self.__table_name} where {Column.id} = ?"  # noqa: S608
        cursor = await self.__conn.cursor()
        await cursor.execute(query, (server_id,))

        result = await cursor.fetchone()

        await cursor.close()
        return result[0] if result else None

    async def set_trigger_emoji(self, server_id: str, trigger_emoji: str) -> None:
        await self.__set_column_value(server_id, Column.trigger_emoji, trigger_emoji)

    async def set_emoji_reaction_threshhold(
        self,
        server_id: str,
        threshhold: int,
    ) -> None:
        await self.__set_column_value(
            server_id,
            Column.emoji_reaction_threshhold,
            str(threshhold),
        )

    async def set_x_bearer_token(self, server_id: str, x_bearer_token: str) -> None:
        await self.__set_column_value(server_id, Column.x_bearer_token, x_bearer_token)

    async def set_x_api_key(self, server_id: str, x_api_key: str) -> None:
        await self.__set_column_value(server_id, Column.x_api_key, x_api_key)

    async def set_x_api_key_secret(self, server_id: str, x_api_key_secret: str) -> None:
        await self.__set_column_value(
            server_id,
            Column.x_api_key_secret,
            x_api_key_secret,
        )

    async def set_x_access_token(self, server_id: str, x_access_token: str) -> None:
        await self.__set_column_value(server_id, Column.x_access_token, x_access_token)

    async def set_x_access_token_secret(
        self,
        server_id: str,
        x_access_token_secret: str,
    ) -> None:
        await self.__set_column_value(
            server_id,
            Column.x_access_token_secret,
            x_access_token_secret,
        )

    async def get_trigger_emoji(self, server_id: str) -> str | None:
        return await self.__get_column_value(server_id, Column.trigger_emoji)

    async def get_emoji_reaction_threshhold(self, server_id: str) -> int | None:
        maybe_threshhold = await self.__get_column_value(
            server_id,
            Column.emoji_reaction_threshhold,
        )
        return int(maybe_threshhold) if maybe_threshhold else None

    async def get_x_auth_bundle(self, server_id: str) -> x.AuthenticationBundle | None:
        """Returns None if any of the auth columns are empty"""
        auth_columns = (
            Column.x_bearer_token,
            Column.x_api_key,
            Column.x_api_key_secret,
            Column.x_access_token,
            Column.x_access_token_secret,
        )

        query = f"""SELECT
            {",".join(auth_columns)}
            FROM {self.__table_name} where {Column.id} = ?
        """  # noqa: S608

        cursor = await self.__conn.cursor()

        await cursor.execute(query, (server_id,))
        result = await cursor.fetchone()
        if result is None or any(x is None for x in result):
            self.__logger.error(
                "Requested auth bundle for server '%s' is incomplete",
                server_id,
            )
            return None

        column_values = dict(zip(auth_columns, result, strict=True))

        await cursor.close()
        return x.AuthenticationBundle(
            bearer_token=column_values[Column.x_bearer_token],
            api_key=column_values[Column.x_api_key],
            api_key_secret=column_values[Column.x_api_key_secret],
            access_token=column_values[Column.x_access_token],
            access_token_secret=column_values[Column.x_access_token_secret],
        )
