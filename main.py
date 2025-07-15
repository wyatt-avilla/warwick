import logging


def main() -> None:
    logging.basicConfig(level=logging.INFO)

    logger = logging.getLogger(__name__)
    logger.info("hello world")


if __name__ == "__main__":
    main()
