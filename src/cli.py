import asyncio

from db import db_connection
from repository.user import UserRepository
from services.user import UsersStatus


async def run():
    async with db_connection() as connection:
        await UsersStatus(
            UserRepository(connection)
        ).check()


def main():
    asyncio.run(run())


if __name__ == "__main__":
    main()
