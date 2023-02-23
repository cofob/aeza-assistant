"""Main entry point for the bot."""

from logging import basicConfig
from os import environ
from sys import argv, exit
from aiohttp import ClientSession
from asyncio import run, get_event_loop

from .bot import BotFabric


def get_env(name: str) -> str:
    """Get environment variable or raise exception."""
    try:
        return environ[name]
    except KeyError:
        print(f"Error: Environment variable {name} is not set, but required.")
        exit(1)


async def main_async() -> None:
    """Run the bot."""
    basicConfig(level=environ.get("LOG_LEVEL", "INFO").upper())
    if len(argv) < 2:
        print("Usage: python -m bot [run]")
        exit(1)

    async with ClientSession() as session:
        bot = BotFabric(
            token=get_env("TOKEN"),
            aeza_token=get_env("AEZA_TOKEN"),
            data_dir=environ.get("DATA_DIR", "data"),
            session=session,
        )

        if argv[1] == "run":
            await bot.run()
        else:
            print("Usage: python -m bot [run]")
            exit(1)


def main() -> None:
    """Run the bot."""
    loop = get_event_loop()
    loop.run_until_complete(main_async())


if __name__ == "__main__":
    main()
