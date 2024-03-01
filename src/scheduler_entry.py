import httpx
import asyncio
import time

import redis
from pytz import utc
from loguru import logger
from settings.cached_settings import CachedSettings
from settings.env_file_settings import EnvFileSettings
from apscheduler.schedulers.background import BackgroundScheduler
from settings.settings import BASE_DIR
from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from srv.events.sink import RabbitmqSink


async def myfunc():
    settings = CachedSettings(EnvFileSettings(BASE_DIR.parent / '.env'))
    rabbitmq_sink = await RabbitmqSink(settings, logger).send(
        'quranbot.mailings',
        {},
        'Mailing.DailyAyats',
        1,
    )


async def main():
    settings = CachedSettings(EnvFileSettings(BASE_DIR.parent / '.env'))
    redis_settings = httpx.URL(settings.REDIS_DSN)
    jobstores = {
        'default': RedisJobStore(
            host=redis_settings.host,
            port=redis_settings.port,
            db=0,
            username=redis_settings.username,
            password=redis_settings.password,
        ),
    }
    scheduler = AsyncIOScheduler(jobstores=jobstores)
    # job = scheduler.add_job(myfunc, 'cron', hour='7')
    job = scheduler.add_job(myfunc, 'interval', minutes=1)
    scheduler.start()
    logger.info("Starting the scheduler...")
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logger.info("Stopping the scheduler...")
        job.remove()
        scheduler.shutdown()


asyncio.run(main())
