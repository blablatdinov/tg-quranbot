import json

from app_types.stringable import Stringable


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
        """
        parsed_json = json.loads(str(self._raw))
        return parsed_json['result'][0]['callback_query']['data']
