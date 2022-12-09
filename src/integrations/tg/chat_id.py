import re

from app_types.intable import Intable
from app_types.stringable import Stringable
from exceptions.base_exception import InternalBotError


class TgChatId(Intable):
    """Идентификатор чата."""

    def __init__(self, update: Stringable):
        """Конструктор класса.

        :param update: Stringable
        """
        self._update = update

    def __int__(self):
        """Числовое представление.

        :return: int
        :raises InternalBotError: В случае отсутсвия идентификатора чата в json
        """
        chat_json_object = re.search('chat":({.+?})', str(self._update))
        if not chat_json_object:
            raise InternalBotError
        chat_id_regex_result = re.search(r'id":(\d+)', chat_json_object.group(1))
        if not chat_id_regex_result:
            raise InternalBotError
        return int(chat_id_regex_result.group(1))
