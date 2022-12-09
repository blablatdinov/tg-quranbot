import re

from app_types.intable import Intable
from app_types.stringable import Stringable
from exceptions.base_exception import InternalBotError


class UpdateId(Intable):
    """Идентификатор обновления."""

    def __init__(self, raw_json: Stringable):
        """Конструктор класса.

        :param raw_json: Stringable
        """
        self._raw = raw_json

    def __int__(self):
        """Числовое представление.

        :return: int
        :raises InternalBotError: если не удалось получить идентификатор обновления
        """
        regex_result = re.search(r'update_id"(:|: )(\d+)', str(self._raw))
        if not regex_result:
            raise InternalBotError
        return int(regex_result.group(2))
