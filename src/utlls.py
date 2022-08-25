from aiogram import Bot

from settings import settings


class BotInstance(object):
    """Класс для хранения и раздачи экземпляра Bot."""

    _bot: Bot = None

    @classmethod
    def get(cls) -> Bot:
        """Получить экземпляр.

        :return: Bot
        """
        if cls._bot:
            return cls._bot
        return Bot(token=settings.API_TOKEN, parse_mode='HTML')


def get_bot_instance() -> Bot:
    """Возарщает экземпляр бота.

    :returns: Bot
    """
    return Bot(token=settings.API_TOKEN, parse_mode='HTML')
