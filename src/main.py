import asyncio

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
from integrations.tg.tg_answers.empty_answer import TgEmptyAnswer
from repository.podcast import PodcastRepository
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
            PodcastAnswer(
                settings.DEBUG,
                empty_answer,
                PodcastRepository(database),
            ),
        ),
    ).run()


if __name__ == '__main__':
    asyncio.run(main())
