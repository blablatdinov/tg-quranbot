"""The MIT License (MIT).

Copyright (c) 2018-2024 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
OR OTHER DEALINGS IN THE SOFTWARE.
"""
import sys

import sentry_sdk
from redis import asyncio as aioredis
from loguru import logger

from db.connection import pgsql
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
from schedule_app import CheckUsersStatus
from services.cli_app import CliApp, CommandCliApp, ForkCliApp
from services.logged_answer import LoggedAnswer
from settings.cached_settings import CachedSettings
from settings.env_file_settings import EnvFileSettings
from settings.settings import BASE_DIR
from srv.events.ayat_changed_event import RbmqAyatChangedEvent
from srv.events.event_hook import EventHookApp, RbmqEventHook
from srv.events.recieved_event import EventFork
from srv.events.sink import FkSink


def main(sys_args: list[str]) -> None:
    """Точка входа в приложение.

    :param sys_args: list[str]
    """
    nats_sink = FkSink()
    settings = CachedSettings(EnvFileSettings(BASE_DIR.parent / '.env'))
    if settings.SENTRY_DSN:
        sentry_sdk.init(
            dsn=settings.SENTRY_DSN,
            enable_tracing=True,
        )
    quranbot_polling_app = CliApp(
        DatabaseConnectedApp(
            pgsql,
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
                            TgMeasureAnswer(
                                QuranbotAnswer(
                                    pgsql,
                                    aioredis.from_url(str(settings.REDIS_DSN)),
                                    nats_sink,
                                    settings,
                                    logger,
                                ),
                                logger,
                            ),
                            logger,
                        ),
                        nats_sink,
                    ),
                    logger,
                ),
                settings.API_TOKEN,
                logger,
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
                    pgsql,
                    CheckUsersStatus(
                        pgsql,
                        TgEmptyAnswer(settings.API_TOKEN),
                        logger,
                    ),
                ),
            ),
        ),
        CommandCliApp(
            'receive_events',
            EventHookApp(
                RbmqEventHook(
                    settings,
                    pgsql,
                    EventFork('Ayat.Changed', 1, RbmqAyatChangedEvent(pgsql)),
                    logger,
                ),
            ),
        ),
    ).run(sys_args)


if __name__ == '__main__':
    main(sys.argv)
