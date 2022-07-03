from aiogram import Dispatcher, executor

from handlers.register import register_handlers
from utlls import get_bot_instance

bot = get_bot_instance()
dp = Dispatcher(bot)


if __name__ == '__main__':
    register_handlers(dp)
    executor.start_polling(dp, skip_updates=True)
