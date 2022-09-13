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
from integrations.tg.tg_answers.empty_answer import TgEmptyAnswer
from integrations.tg.tg_answers.markup_answer import TgAnswerMarkup
from integrations.tg.tg_answers.message_regex_answer import MessageRegexAnswer
from repository.podcast import RandomPodcast
from services.answers.answer import DefaultKeyboard
from services.podcast_answer import PodcastAnswer
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
            ),
        ),
    ).run()


if __name__ == '__main__':
    with suppress(KeyboardInterrupt):
        asyncio.run(main())
