import asyncio
import datetime
import sys

from db.connection import DBConnection, database
from exceptions.base_exception import BaseAppError
from integrations.event_handlers.mailing_created import MailingCreatedEvent
from integrations.event_handlers.messages_deleted import MessagesDeletedEvent
from integrations.event_handlers.notification_created import NotificationCreatedEvent
from integrations.nats_integration import NatsIntegration
from repository.ayats.ayat_morning_content import AyatMorningContentRepository
from repository.mailing import MailingRepository
from repository.prayer_time import PrayerTimeRepository
from repository.update_log import UpdatesLogRepository
from repository.users.user import UserRepository
from repository.users.users import UsersRepository
from services.answers.spam_answer_list import SavedSpamAnswerList
from services.ayats.morning_spam import MorningSpam
from services.mailing_with_notification import MailingWithNotification
from services.prayers.prayer_status_markup import PrayerTimeKeyboard
from services.prayers.prayer_times import PrayerForUserAnswer, PrayerTimes, UserPrayerTimes
from services.user import UsersStatus
from services.users_day import MailingWithUpdateUserDays
from utlls import BotInstance


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
                        AyatMorningContentRepository(connection),
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
    chat_ids = await UsersRepository(database).active_users_with_city()
    for chat_id in chat_ids:
        await PrayerForUserAnswer(
            BotInstance.get(),
            chat_id,
            PrayerTimes(
                chat_id,
                UserRepository(database),
                PrayerTimeRepository(database),
                datetime.datetime.today(),
            ),
            PrayerTimeKeyboard(
                UserPrayerTimes(
                    chat_id,
                    PrayerTimes(
                        chat_id,
                        UserRepository(database),
                        PrayerTimeRepository(database),
                        datetime.datetime.today(),
                    ),
                    UserRepository(database),
                    PrayerTimeRepository(database),
                ),
            ),
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
