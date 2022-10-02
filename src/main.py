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
from integrations.tg.tg_answers import TgEmptyAnswer, TgMeasureAnswer, TgMessageAnswer
from quranbot_answer import QuranbotAnswer
from services.append_update_id_answer import AppendDebugInfoAnswer, UpdateIdDebugParam, \
    ChatIdDebugParam, TimeDebugParam, CommitHashDebugParam
from settings import settings


async def main() -> None:
    """Точка входа в приложение."""
    redis = await aioredis.from_url(str(settings.REDIS_DSN))  # type: ignore
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
            AppendDebugInfoAnswer(
                settings.DEBUG,
                TgMeasureAnswer(
                    QuranbotAnswer(empty_answer, message_answer, database, redis),
                ),
                UpdateIdDebugParam(),
                ChatIdDebugParam(),
                TimeDebugParam(),
                CommitHashDebugParam(settings.BASE_DIR.parent),
            )
        ),
    ).run()


if __name__ == '__main__':
    with suppress(KeyboardInterrupt):
        asyncio.run(main())
