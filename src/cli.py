import asyncio
import datetime
import sys

from db import DBConnection
from exceptions.base_exception import BaseAppError
from integrations.event_handlers.notification_created import NotificationCreatedEvent
from integrations.nats_integration import MailingCreatedEvent, MessagesDeletedEvent, NatsIntegration
from repository.ayats.ayat_spam import AyatSpamRepository
from repository.mailing import MailingRepository
from repository.prayer_time import PrayerTimeRepository
from repository.update_log import UpdatesLogRepository
from repository.users.user import UserRepository
from repository.users.users import UsersRepository
from services.answers.log_answer import LoggedAnswer
from services.answers.spam_answer_list import SavedSpamAnswerList
from services.ayats.morning_spam import MorningSpam
from services.mailing_with_notification import MailingWithNotification
from services.prayer_time import PrayerTimes, UserPrayerTimes, UserPrayerTimesAnswer
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
        await MailingWithNotification(
            SavedSpamAnswerList(
                MailingWithUpdateUserDays(
                    MorningSpam(
                        AyatSpamRepository(connection),
                        UsersRepository(connection),
                    ),
                    UsersRepository(connection),
                ),
                MailingRepository(
                    connection,
                    UpdatesLogRepository(connection),
                ),
            ),
            NatsIntegration([]),
        ).send()


async def send_prayer_time() -> None:
    """Отправить времена намазов для след. дня."""
    async with DBConnection() as connection:
        chat_ids = await UsersRepository(connection).get_active_user_chat_ids()
        for chat_id in chat_ids:
            await LoggedAnswer(
                await UserPrayerTimesAnswer(
                    UserPrayerTimes(
                        PrayerTimes(
                            prayer_times_repository=PrayerTimeRepository(connection),
                            user_repository=UserRepository(connection),
                            chat_id=chat_id,
                        ),
                        datetime.datetime.now() + datetime.timedelta(days=1),
                    ),
                    datetime.datetime.now() + datetime.timedelta(days=1),
                ).to_answer(),
                UpdatesLogRepository(connection),
            ).send(chat_id)


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
                NotificationCreatedEvent(
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
        'prayers': send_prayer_time,
    }.get(sys.argv[1])

    if not func:
        raise BaseAppError

    asyncio.run(func())


if __name__ == '__main__':
    main()
