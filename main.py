import asyncio
import logging
from pathlib import Path

from database import DatabaseInterface


async def main() -> None:
    logging.basicConfig(level=logging.INFO)

    logger = logging.getLogger(__name__)
    logger.info("hello world")

    async with await DatabaseInterface.new(Path("warwick.db")) as db:
        logger.info("Using '%s' as database", db.database_file)


if __name__ == "__main__":
    asyncio.run(main())
