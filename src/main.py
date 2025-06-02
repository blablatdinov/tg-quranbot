# The MIT License (MIT).
#
# Copyright (c) 2018-2025 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
# OR OTHER DEALINGS IN THE SOFTWARE.

import sys

import sentry_sdk
from loguru import logger
from redis import asyncio as aioredis

from db.connection import pgsql
from integrations.tg.app_with_get_me import AppWithGetMe
from integrations.tg.database_connected_app import DatabaseConnectedApp
from integrations.tg.polling_app import PollingApp
from integrations.tg.polling_updates import PollingUpdatesIterator
from integrations.tg.sendable_answer import SendableAnswer
from integrations.tg.tg_answers import TgEmptyAnswer, TgMeasureAnswer
from integrations.tg.udpates_with_offset_url import UpdatesWithOffsetURL
from integrations.tg.updates_timeout import UpdatesTimeout
from integrations.tg.updates_url import UpdatesURL
from integrations.tg.upddates_long_pollinig_url import UpdatesLongPollingURL
from quranbot_answer import QuranbotAnswer
from services.cli_app import CliApp
from services.command_cli_app import CommandCliApp
from services.fork_cli_app import ForkCliApp
from services.logged_answer import LoggedAnswer
from settings import BASE_DIR, Settings
from srv.events.ayat_changed_event import RbmqAyatChangedEvent
from srv.events.check_user_status import CheckUsersStatus
from srv.events.event_fork import EventFork
from srv.events.event_hook_app import EventHookApp
from srv.events.mailing_created import MailingCreatedEvent
from srv.events.message_deleted import MessageDeleted
from srv.events.morning_content_published import MorningContentPublishedEvent
from srv.events.prayer_created_event import PrayerCreatedEvent
from srv.events.prayers_mailing import PrayersMailingPublishedEvent
from srv.events.rabbitmq_sink import RabbitmqSink
from srv.events.rbmq_event_hook import RbmqEventHook
from metrics.measured_answer import MeasuredAnswer
from prometheus_client import start_http_server, Counter, Summary, Gauge


def main(sys_args: list[str]) -> None:
    """Точка входа в приложение.

    :param sys_args: list[str]
    """
    settings = Settings(_env_file=BASE_DIR.parent / '.env')
    rabbitmq_sink = RabbitmqSink(settings, logger)
    redis = aioredis.from_url(str(settings.REDIS_DSN))
    if settings.SENTRY_DSN:
        sentry_sdk.init(
            dsn=settings.SENTRY_DSN,
            enable_tracing=True,
        )
    start_http_server(9091)
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
                                MeasuredAnswer(
                                    QuranbotAnswer.ctor(
                                        pgsql,
                                        redis,
                                        rabbitmq_sink,
                                        settings,
                                        logger,
                                    ),
                                ),
                                logger,
                            ),
                            logger,
                        ),
                        rabbitmq_sink,
                    ),
                    logger,
                ),
                settings.API_TOKEN,
                logger,
            ),
        ),
    )
    ForkCliApp.ctor(
        CommandCliApp(
            'run_polling',
            quranbot_polling_app,
        ),
        CommandCliApp(
            'receive_events',
            EventHookApp(
                RbmqEventHook.ctor(
                    settings,
                    pgsql,
                    logger,
                    EventFork('Ayat.Changed', 1, RbmqAyatChangedEvent(pgsql)),
                    EventFork('Mailing.DailyAyats', 1, MorningContentPublishedEvent(
                        TgEmptyAnswer(settings.API_TOKEN),
                        pgsql,
                        settings,
                        rabbitmq_sink,
                        logger,
                    )),
                    EventFork('Mailing.DailyPrayers', 1, PrayersMailingPublishedEvent(
                        TgEmptyAnswer(settings.API_TOKEN),
                        pgsql,
                        settings,
                        rabbitmq_sink,
                        logger,
                        redis,
                    )),
                    EventFork('Mailing.Created', 1, MailingCreatedEvent(
                        TgEmptyAnswer(settings.API_TOKEN),
                        pgsql,
                        rabbitmq_sink,
                        logger,
                        settings,
                    )),
                    EventFork('User.CheckStatus', 1, CheckUsersStatus(
                        TgEmptyAnswer(settings.API_TOKEN),
                        pgsql,
                        rabbitmq_sink,
                        logger,
                    )),
                    EventFork('Messages.Deleted', 2, MessageDeleted(
                        TgEmptyAnswer(settings.API_TOKEN),
                        pgsql,
                        rabbitmq_sink,
                        logger,
                    )),
                    EventFork('Prayers.Created', 2, PrayerCreatedEvent(pgsql)),
                ),
            ),
        ),
    ).run(sys_args)


if __name__ == '__main__':
    main(sys.argv)
