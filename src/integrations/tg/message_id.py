import re

from app_types.intable import Intable
from app_types.stringable import Stringable
from exceptions.base_exception import InternalBotError


class MessageId(Intable):
    """Идентификатор сообщения."""

    def __init__(self, raw: Stringable):
        """Конструктор класса.

        :param raw: Stringable
        """
        self._raw = raw

    def __int__(self):
        """Числовое представление.

        :return: int
        :raises InternalBotError: если идентификатор сообщения не найден
        """
        regex_result = re.search(r'message_id"(:|: )(\d+)', str(self._raw))
        if not regex_result:
            raise InternalBotError
        return int(regex_result.group(2))
