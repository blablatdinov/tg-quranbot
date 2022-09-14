import asyncio
from contextlib import suppress

from db.connection import database
from integrations.tg.app import PollingApp
from integrations.tg.polling_updates import (
    PollingUpdatesIterator,
    UpdatesLongPollingURL,
    UpdatesTimeout,
    UpdatesURL,
    UpdatesWithOffsetURL,
)
from integrations.tg.sendable import SendableAnswer
from integrations.tg.tg_answers.answer_fork import AnswerFork
from integrations.tg.tg_answers.answer_to_sender import TgAnswerToSender
from integrations.tg.tg_answers.callback_query_regex_answer import CallbackQueryRegexAnswer
from integrations.tg.tg_answers.empty_answer import TgEmptyAnswer
from integrations.tg.tg_answers.markup_answer import TgAnswerMarkup
from integrations.tg.tg_answers.message_answer import TgMessageAnswer
from integrations.tg.tg_answers.message_keyboard_edit_answer import TgKeyboardEditAnswer
from integrations.tg.tg_answers.message_regex_answer import MessageRegexAnswer
from repository.podcast import RandomPodcast
from repository.prayer_time import NewUserPrayers, PrayersWithoutSunrise, SafeUserPrayers, UserPrayers
from services.answers.answer import DefaultKeyboard
from services.podcast_answer import PodcastAnswer
from services.prayers.prayer_status import UserPrayerStatus
from services.prayers.prayer_times import PrayerForUserAnswer, UserPrayerStatusChangeAnswer
from settings import settings


async def main():
    """Точка входа в приложение."""
    empty_answer = TgEmptyAnswer(settings.API_TOKEN)
    await database.connect()
    await PollingApp(
        PollingUpdatesIterator(
            UpdatesLongPollingURL(
                UpdatesWithOffsetURL(
                    UpdatesURL(settings.API_TOKEN),
                ),
                UpdatesTimeout(),
            ),
            UpdatesTimeout(),
        ),
        SendableAnswer(
            AnswerFork(
                MessageRegexAnswer(
                    'Подкасты',
                    TgAnswerMarkup(
                        PodcastAnswer(
                            settings.DEBUG,
                            empty_answer,
                            RandomPodcast(database),
                        ),
                        DefaultKeyboard(),
                    ),
                ),
                MessageRegexAnswer(
                    'Время намаза',
                    PrayerForUserAnswer(
                        TgAnswerToSender(
                            TgMessageAnswer(
                                empty_answer,
                            ),
                        ),
                        SafeUserPrayers(
                            UserPrayers(database),
                            NewUserPrayers(
                                database,
                                PrayersWithoutSunrise(
                                    UserPrayers(database),
                                ),
                            ),
                        ),
                    ),
                ),
                CallbackQueryRegexAnswer(
                    '(mark_readed|mark_not_readed)',
                    UserPrayerStatusChangeAnswer(
                        TgAnswerToSender(
                            TgKeyboardEditAnswer(
                                empty_answer,
                            ),
                        ),
                        UserPrayerStatus(database),
                        UserPrayers(database),
                    ),
                ),
            ),
        ),
    ).run()


if __name__ == '__main__':
    with suppress(KeyboardInterrupt):
        asyncio.run(main())
