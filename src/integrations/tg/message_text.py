import re

from app_types.stringable import Stringable
from exceptions.base_exception import InternalBotError


class MessageText(Stringable):
    """Текст сообщения."""

    def __init__(self, raw: Stringable):
        """Конструктор класса.

        :param raw: Stringable
        """
        self._raw = raw

    def __str__(self):
        """Строковое представление.

        :return: str
        :raises InternalBotError: если текст сообщения не найден
        """
        regex_res = re.search('text"(:|: )"(.+?)"', str(self._raw))
        if not regex_res:
            raise InternalBotError
        return regex_res.group(2)
