import asyncio
import sys

from db import DBConnection
from exceptions.base_exception import BaseAppError
from integrations.nats_integration import MailingCreatedEvent, MessagesDeletedEvent, NatsIntegration
from repository.ayats.ayat_spam import AyatSpamRepository
from repository.mailing import MailingRepository
from repository.update_log import UpdatesLogRepository
from repository.users.users import UsersRepository
from services.ayats.morning_spam import MorningSpam
from services.user import UsersStatus
from services.users_day import MailingWithUpdateUserDays


async def check_users_status() -> None:
    """Запуск проверки статуса пользователей."""
    async with DBConnection() as connection:
        await UsersStatus(
            UsersRepository(connection),
        ).check()


async def send_morning_content() -> None:
    """Рассылка утреннего контента."""
    async with DBConnection() as connection:
        await MailingWithUpdateUserDays(
            MorningSpam(
                AyatSpamRepository(connection),
                UsersRepository(connection),
            ),
            UsersRepository(connection),
        ).send()


async def start_events_receiver() -> None:
    """Запуск обработки событий из очереди."""
    async with DBConnection() as connection:
        nats_integration = NatsIntegration(
            [
                MailingCreatedEvent(
                    UsersRepository(connection),
                    MailingRepository(connection, UpdatesLogRepository(connection)),
                ),
                MessagesDeletedEvent(
                    UpdatesLogRepository(connection),
                ),
            ],
        )
        await nats_integration.receive()


def main() -> None:
    """Entrypoint.

    :raises BaseAppError: cli errors
    """
    if len(sys.argv) < 2:
        raise BaseAppError

    func = {
        'check': check_users_status,
        'morning-content': send_morning_content,
        'queue': start_events_receiver,
    }.get(sys.argv[1])

    if not func:
        raise BaseAppError

    asyncio.run(func())


if __name__ == '__main__':
    main()
