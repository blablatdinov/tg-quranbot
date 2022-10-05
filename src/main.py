import sys
from contextlib import suppress

import aioredis

from db.connection import database
from integrations.tg.app import PollingApp, DatabaseConnectedApp
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
from services.append_update_id_answer import (
    AppendDebugInfoAnswer,
    ChatIdDebugParam,
    CommitHashDebugParam,
    TimeDebugParam,
    UpdateIdDebugParam,
)
from services.cli_app import CliApp, ForkCliApp, CommandCliApp
from settings import settings


def main() -> None:
    """Точка входа в приложение."""
    empty_answer = TgEmptyAnswer(settings.API_TOKEN)
    message_answer = TgMessageAnswer(empty_answer)
    quranbot_polling_app = CliApp(
        DatabaseConnectedApp(
            database,
            PollingApp(
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
                            QuranbotAnswer(
                                empty_answer,
                                message_answer,
                                database,
                                aioredis.from_url(str(settings.REDIS_DSN)),
                            ),
                        ),
                        UpdateIdDebugParam(),
                        ChatIdDebugParam(),
                        TimeDebugParam(),
                        CommitHashDebugParam(settings.BASE_DIR.parent),
                    ),
                ),
            ),
        ),
    )
    ForkCliApp(
        CommandCliApp(
            'run_polling',
            quranbot_polling_app,
        ),
    ).run(sys.argv)


if __name__ == '__main__':
    with suppress(KeyboardInterrupt):
        main()
