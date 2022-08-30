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
        if not cls._bot:
            cls._bot = Bot(token=settings.API_TOKEN, parse_mode='HTML')
        return cls._bot


def get_bot_instance() -> Bot:
    """Возарщает экземпляр бота.

    :returns: Bot
    """
    return Bot(token=settings.API_TOKEN, parse_mode='HTML')
