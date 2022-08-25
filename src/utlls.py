from aiogram import Bot

from settings import settings


class BotInstance(object):

    _bot: Bot = None

    @classmethod
    def get(cls):
        if cls._bot:
            return cls._bot
        return Bot(token=settings.API_TOKEN, parse_mode='HTML')


def get_bot_instance() -> Bot:
    """Возарщает экземпляр бота.

    :returns: Bot
    """
    return Bot(token=settings.API_TOKEN, parse_mode='HTML')
