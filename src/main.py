import sys
from contextlib import suppress

import aioredis

from db.connection import database
from integrations.tg.app import DatabaseConnectedApp, PollingApp
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
from repository.users.users import UsersRepository
from schedule_app import CheckUsersStatus
from services.append_update_id_answer import (
    AppendDebugInfoAnswer,
    ChatIdDebugParam,
    CommitHashDebugParam,
    TimeDebugParam,
    UpdateIdDebugParam,
)
from services.cli_app import CliApp, CommandCliApp, ForkCliApp
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
                                aioredis.from_url(str(settings.REDIS_DSN)),  # type: ignore
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
        CommandCliApp(
            'check_user_status',
            CliApp(
                DatabaseConnectedApp(
                    database,
                    CheckUsersStatus(
                        UsersRepository(database),
                        empty_answer,
                    ),
                ),
            )
        ),
    ).run(sys.argv)


if __name__ == '__main__':
    with suppress(KeyboardInterrupt):
        main()
