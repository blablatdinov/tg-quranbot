import asyncio
import sys

from db import DBConnection
from exceptions.base_exception import BaseAppError
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
    """Рассылка утреннего контента."""
    async with DBConnection() as connection:
        await MorningSpam(
            AyatSpamRepository(connection),
            UsersRepository(connection),
        ).send()


def main() -> None:
    """Entrypoint.

    :raises BaseAppError: cli errors
    """
    if len(sys.argv) < 2:
        raise BaseAppError

    func = {
        'check': check_users_status,
        'morning-content': send_morning_content,
    }.get(sys.argv[1])

    if not func:
        raise BaseAppError

    asyncio.run(func())


if __name__ == '__main__':
    main()
