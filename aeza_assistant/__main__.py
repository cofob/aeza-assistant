"""Main entry point for the bot."""

from asyncio import run, sleep
from json import loads
from logging import basicConfig
from os import chdir, environ, getcwd, path
from sys import argv, exit

from aiohttp import ClientSession
from alembic.command import upgrade
from alembic.config import Config

from .bot import BotFabric


def get_env(name: str) -> str:
    """Get environment variable or raise exception."""
    try:
        return environ[name]
    except KeyError:
        print(f"Error: Environment variable {name} is not set, but required.")
        exit(1)


def print_help() -> None:
    """Print help."""
    print("Usage: python -m bot [run|notify] <notify:manual statuses json>")


async def main_async() -> None:
    """Run the bot."""
    basicConfig(
        level=environ.get("LOG_LEVEL", "INFO").upper(), filename=environ.get("LOG_FILE")
    )
    if len(argv) < 2:
        print_help()
        exit(1)

    async with ClientSession(trust_env=True) as session:
        bot = BotFabric(
            token=get_env("TOKEN"),
            database_url=get_env("DATABASE_URL"),
            push_addresses=environ.get("PUSH_ADDRESSES", ""),
            aeza_http_proxy=environ.get("AEZA_HTTP_PROXY", None),
            session=session,
        )

        if argv[1] == "run":
            await bot.run()
        elif argv[1] == "notify":
            statuses = loads(argv[2])
            async with bot.cron.maker() as db:
                await bot.cron.send_notification(db, statuses)
            await bot.task_queue.start()
            while True:
                await sleep(1)
                if bot.task_queue.queue.empty():
                    break
        else:
            print_help()
            exit(1)


def main() -> None:
    """Run the bot."""
    if argv[1] == "migrate":
        lib_dir = path.dirname(path.abspath(__file__))
        alembic_ini_path = path.join(lib_dir, "alembic.ini")
        config = Config(alembic_ini_path)
        cwd = getcwd()
        chdir(lib_dir)
        upgrade(config, "head")
        chdir(cwd)
    else:
        run(main_async())


if __name__ == "__main__":
    main()
