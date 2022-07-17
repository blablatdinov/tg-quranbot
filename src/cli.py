import asyncio
import sys

from db import DBConnection
from repository.ayats.ayat_spam import AyatSpamRepository
from repository.users.users import UsersRepository
from services.ayats.morning_spam import MorningSpam
from services.user import UsersStatus


async def check_users_status() -> None:
    """Запуск проверки статуса пользователей."""
    async with DBConnection() as connection:
        await UsersStatus(
            UsersRepository(connection),
        ).check()


async def send_morning_content() -> None:
    async with DBConnection() as connection:
        await MorningSpam(
            AyatSpamRepository(connection),
            UsersRepository(connection),
        ).send()


def main() -> None:
    """Entrypoint."""
    if len(sys.argv) < 2:
        raise Exception

    print(sys.argv)

    func = {
        'check': check_users_status,
        'morning-content': send_morning_content,
    }.get(sys.argv[1])

    if not func:
        raise Exception

    asyncio.run(func())


if __name__ == '__main__':
    main()
