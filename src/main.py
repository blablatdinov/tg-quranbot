import sys
from contextlib import suppress

from redis import asyncio as aioredis

from db.connection import database
from event_recieve import RecievedEvents
from integrations.event_handlers.prayers_sended import SendPrayersEvent
from integrations.nats_integration import NatsSink
from integrations.tg.app import AppWithGetMe, DatabaseConnectedApp, PollingApp
from integrations.tg.polling_updates import (
    PollingUpdatesIterator,
    UpdatesLongPollingURL,
    UpdatesTimeout,
    UpdatesURL,
    UpdatesWithOffsetURL,
)
from integrations.tg.sendable import SendableAnswer
from integrations.tg.tg_answers import TgEmptyAnswer, TgMeasureAnswer
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
from services.logged_answer import LoggedAnswer
from settings import settings


def main() -> None:
    """Точка входа в приложение."""
    nats_sink = NatsSink()
    quranbot_polling_app = CliApp(
        DatabaseConnectedApp(
            database,
            AppWithGetMe(
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
                    LoggedAnswer(
                        SendableAnswer(
                            AppendDebugInfoAnswer(
                                settings.DEBUG,
                                TgMeasureAnswer(
                                    QuranbotAnswer(
                                        database,
                                        aioredis.from_url(str(settings.REDIS_DSN)),  # type: ignore
                                        nats_sink,
                                    ),
                                ),
                                UpdateIdDebugParam(),
                                ChatIdDebugParam(),
                                TimeDebugParam(),
                                CommitHashDebugParam(''),
                            ),
                        ),
                        nats_sink,
                    ),
                ),
                settings.API_TOKEN,
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
                        TgEmptyAnswer(settings.API_TOKEN),
                    ),
                ),
            ),
        ),
        CommandCliApp(
            'recieve_events',
            CliApp(
                DatabaseConnectedApp(
                    database,
                    RecievedEvents(
                        SendPrayersEvent(
                            UsersRepository(database),
                            TgEmptyAnswer(settings.API_TOKEN),
                            database,
                        ),
                    ),
                ),
            ),
        ),
    ).run(sys.argv)


if __name__ == '__main__':
    with suppress(KeyboardInterrupt):
        main()
