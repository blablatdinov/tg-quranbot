import json

from app_types.stringable import Stringable
from exceptions.internal_exceptions import CallbackQueryNotFoundError


class CallbackQueryData(Stringable):
    """Информация с кнопки."""

    def __init__(self, raw: Stringable):
        """Конструктор класса.

        :param raw: Stringable
        """
        self._raw = raw

    def __str__(self):
        """Строковое представление.

        :return: str
        :raises CallbackQueryNotFoundError: если не удалось получить данные с кнопки
        """
        parsed_json = json.loads(str(self._raw))
        try:
            return parsed_json['result'][0]['callback_query']['data']
        except KeyError as err:
            raise CallbackQueryNotFoundError from err
