import asyncio
from contextlib import suppress

import aioredis

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
from integrations.tg.tg_answers import TgMeasureAnswer, TgEmptyAnswer, TgMessageAnswer
from quranbot_answer import QuranbotAnswer
from settings import settings


async def main() -> None:
    """Точка входа в приложение."""
    redis = await aioredis.from_url(str(settings.REDIS_DSN))
    empty_answer = TgEmptyAnswer(settings.API_TOKEN)
    message_answer = TgMessageAnswer(empty_answer)
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
            TgMeasureAnswer(
                QuranbotAnswer(empty_answer, message_answer, database, redis),
            ),
        ),
    ).run()


if __name__ == '__main__':
    with suppress(KeyboardInterrupt):
        asyncio.run(main())
