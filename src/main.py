import logging

from aiogram import Dispatcher, executor, types
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from aiogram.utils.executor import start_webhook

from handlers.register import register_handlers
from settings import settings
from aiogram.dispatcher.webhook import SendMessage
from utlls import get_bot_instance

bot = get_bot_instance()
state_storage = RedisStorage2(settings.REDIS_HOST, settings.REDIS_PORT, db=settings.REDIS_DB)
dp = Dispatcher(bot, storage=state_storage)

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',  # noqa: WPS323 logger formatting
)

WEBHOOK_HOST = '88.218.170.214'
WEBHOOK_PATH = '/bot'
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"
WEBAPP_HOST = 'localhost'
WEBAPP_PORT = 8010


async def on_startup(dp):
    logging.warning('Setting webhook...')
    res = await bot.set_webhook(WEBHOOK_URL)
    logging.warning('Setting webhook res: %s', res)


async def on_shutdown(dp):
    logging.warning('Shutting down..')
    await bot.delete_webhook()
    await dp.storage.close()
    await dp.storage.wait_closed()
    logging.warning('Bye!')


if __name__ == '__main__':
    register_handlers(dp)
    if settings.DEBUG:
        executor.start_polling(dp, skip_updates=True)
    else:
        start_webhook(
            dispatcher=dp,
            webhook_path=WEBHOOK_PATH,
            on_startup=on_startup,
            on_shutdown=on_shutdown,
            skip_updates=True,
            host=WEBAPP_HOST,
            port=WEBAPP_PORT,
        )
