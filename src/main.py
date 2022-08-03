import logging

from aiogram import Dispatcher, executor
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from aiogram.utils.executor import start_webhook
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from cli import check_users_status, send_morning_content, send_prayer_time
from handlers.register import register_handlers
from settings import settings
from utlls import get_bot_instance

bot = get_bot_instance()
state_storage = RedisStorage2(settings.REDIS_HOST, settings.REDIS_PORT, db=settings.REDIS_DB)
dp = Dispatcher(bot, storage=state_storage)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',  # noqa: WPS323 logger formatting
)
scheduler = AsyncIOScheduler()


async def on_startup(dispatcher: Dispatcher):
    """Действия, выполняемые при старте приложения.

    :param dispatcher: Dispatcher
    """
    await bot.set_webhook(settings.webhook_url)


async def on_shutdown(dispatcher: Dispatcher):
    """Действия, выполняемые при остановке приложения.

    :param dispatcher: Dispatcher
    """
    logging.warning('Shutting down..')
    await bot.delete_webhook()
    await dp.storage.close()
    await dp.storage.wait_closed()
    logging.warning('Bye!')


scheduler.add_job(send_morning_content, trigger='cron', hour='7')
scheduler.add_job(check_users_status, trigger='cron', hour='6')
scheduler.add_job(send_prayer_time, trigger='cron', hour='20')


if __name__ == '__main__':
    register_handlers(dp)
    scheduler.start()
    if settings.DEBUG:
        executor.start_polling(dp, skip_updates=True)
    else:
        start_webhook(
            dispatcher=dp,
            webhook_path=settings.WEBHOOK_PATH,
            on_startup=on_startup,
            on_shutdown=on_shutdown,
            skip_updates=True,
            host=settings.WEBAPP_HOST,
            port=settings.WEBAPP_PORT,
        )
