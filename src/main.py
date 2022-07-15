import logging

from aiogram import Dispatcher, executor
from aiogram.contrib.fsm_storage.redis import RedisStorage2

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


if __name__ == '__main__':
    register_handlers(dp)
    executor.start_polling(dp, skip_updates=True)
