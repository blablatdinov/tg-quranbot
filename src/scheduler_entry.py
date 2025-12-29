# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

import asyncio
import logging

import httpx
from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from loguru import logger

from settings import settings
from srv.events.rabbitmq_sink import RabbitmqSink

logging.basicConfig()
logging.getLogger('apscheduler').setLevel(logging.DEBUG)


async def _morning_ayats_task() -> None:  # noqa: NPM100. Fix it
    await RabbitmqSink(settings, logger).send(
        'quranbot.mailings',
        {},
        'Mailing.DailyAyats',
        1,
    )


async def _daily_prayers_task() -> None:  # noqa: NPM100. Fix it
    await RabbitmqSink(settings, logger).send(
        'quranbot.mailings',
        {},
        'Mailing.DailyPrayers',
        1,
    )


async def _daily_check_user_status() -> None:  # noqa: NPM100. Fix it
    await RabbitmqSink(settings, logger).send(
        'quranbot.users',
        {},
        'User.CheckStatus',
        1,
    )


async def main() -> None:
    """Entrypoint."""
    redis_settings = httpx.URL(str(settings.REDIS_DSN))
    jobstores = {
        'default': RedisJobStore(
            host=redis_settings.host,
            port=redis_settings.port,
            db=0,
            username=redis_settings.username,
            password=redis_settings.password,
        ),
    }
    scheduler = AsyncIOScheduler(jobstores=jobstores, timezone='Europe/Moscow')
    scheduler.start()
    logger.info('Starting the scheduler...')
    try:
        while True:  # noqa: WPS457, ASYNC110
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logger.info('Stopping the scheduler...')
        scheduler.shutdown()


if __name__ == '__main__':
    asyncio.run(main())
