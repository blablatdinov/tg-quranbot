from aiogram import Bot

from settings import settings


def get_bot_instance() -> Bot:
    """Возарщает экземпляр бота.

    :returns: Bot
    """
    return Bot(token=settings.API_TOKEN, parse_mode='HTML')
