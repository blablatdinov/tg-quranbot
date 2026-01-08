# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

import sys

import sentry_sdk
from loguru import logger
from prometheus_client import start_http_server
from redis import asyncio as aioredis

from db.connection import pgsql
from integrations.tg.app_with_get_me import AppWithGetMe
from integrations.tg.database_connected_app import DatabaseConnectedApp
from integrations.tg.polling_app import PollingApp
from integrations.tg.polling_updates import PollingUpdatesIterator
from integrations.tg.sendable_answer import SendableAnswer
from integrations.tg.tg_answers import TgEmptyAnswer, TgMeasureAnswer
from integrations.tg.udpates_with_offset_url import UpdatesWithOffsetURL
from integrations.tg.updates_long_polling_url import UpdatesLongPollingURL
from integrations.tg.updates_timeout import UpdatesTimeout
from integrations.tg.updates_url import UpdatesURL
from metrics.measured_answer import MeasuredAnswer
from metrics.prometheus import BOT_REQUESTS
from quranbot_answer import QuranbotAnswer
from services.cli_app import CliApp
from services.command_cli_app import CommandCliApp
from services.fork_cli_app import ForkCliApp
from services.logged_answer import LoggedAnswer
from settings import settings
from srv.events.ayat_changed_event import RbmqAyatChangedEvent
from srv.events.check_user_status import CheckUsersStatus
from srv.events.event_fork import EventFork
from srv.events.event_hook_app import EventHookApp
from srv.events.fk_sink import FkSink
from srv.events.mailing_created import MailingCreatedEvent
from srv.events.message_deleted import MessageDeleted
from srv.events.morning_content_published import MorningContentPublishedEvent
from srv.events.prayer_created_event import PrayerCreatedEvent
from srv.events.prayers_mailing import PrayersMailingPublishedEvent
from srv.events.rabbitmq_sink import RabbitmqSink
from srv.events.rbmq_event_hook import RbmqEventHook


def main(sys_args: list[str]) -> None:
    """Точка входа в приложение.

    :param sys_args: list[str]
    """
    sink = RabbitmqSink(settings, logger) if settings.SINK_ENABLE else FkSink()
    redis = aioredis.from_url(str(settings.REDIS_DSN))
    if settings.SENTRY_DSN:
        sentry_sdk.init(
            dsn=settings.SENTRY_DSN,
            enable_tracing=True,
        )
    start_http_server(settings.PROMETHEUS_PORT)
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
                                        sink,
                                        settings,
                                        logger,
                                    ),
                                    BOT_REQUESTS,
                                ),
                                logger,
                            ),
                            logger,
                        ),
                        sink,
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
                        sink,
                        logger,
                    )),
                    EventFork('Mailing.DailyPrayers', 1, PrayersMailingPublishedEvent(
                        TgEmptyAnswer(settings.API_TOKEN),
                        pgsql,
                        settings,
                        sink,
                        logger,
                        redis,
                    )),
                    EventFork('Mailing.Created', 1, MailingCreatedEvent(
                        TgEmptyAnswer(settings.API_TOKEN),
                        pgsql,
                        sink,
                        logger,
                        settings,
                    )),
                    EventFork('User.CheckStatus', 1, CheckUsersStatus(
                        TgEmptyAnswer(settings.API_TOKEN),
                        pgsql,
                        sink,
                        logger,
                    )),
                    EventFork('Messages.Deleted', 2, MessageDeleted(
                        TgEmptyAnswer(settings.API_TOKEN),
                        pgsql,
                        sink,
                        logger,
                    )),
                    EventFork('Prayers.Created', 2, PrayerCreatedEvent(pgsql)),
                ),
            ),
        ),
    ).run(sys_args)


if __name__ == '__main__':
    main(sys.argv)
