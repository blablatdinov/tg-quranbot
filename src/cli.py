import asyncio

from db import DBConnection
from repository.user import UserRepository
from services.user import UsersStatus


async def run():
    """Запуск проверки статуса пользователей."""
    async with DBConnection() as connection:
        await UsersStatus(
            UserRepository(connection),
        ).check()


def main():
    """Entrypoint."""
    asyncio.run(run())


if __name__ == '__main__':
    main()
