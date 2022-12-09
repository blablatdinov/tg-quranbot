import re

from app_types.intable import Intable
from app_types.stringable import Stringable, UnwrappedString
from exceptions.internal_exceptions import InlineQueryIdNotFoundError, InlineQueryNotFoundError


class InlineQuery(Stringable):
    """Данные с инлайн поиска."""

    def __init__(self, update: Stringable):
        """Конструктор класса.

        :param update: Stringable
        """
        self._update = update

    def __str__(self):
        """Строковое представление.

        :return: str
        :raises InlineQueryNotFoundError: если не найдены данные инлайн поиска
        """
        unwrapped_string = str(self._update)
        query_regex_result = re.search('query"(:|: )"(.+?)"', unwrapped_string)
        if not query_regex_result:
            raise InlineQueryNotFoundError
        return query_regex_result.group(2)


class InlineQueryId(Intable):
    """Идентификатор инлайн поиска."""

    def __init__(self, update: Stringable):
        """Конструктор класса.

        :param update: Stringable
        """
        self._update = update

    def __int__(self):
        """Числовое представление.

        :return: int
        :raises InlineQueryIdNotFoundError: если не найден идентификатор инлайн поиска
        """
        unwrapped_string = str(UnwrappedString(self._update))
        regex_result = re.search('inline_query"(:|: )({.+?})', unwrapped_string)
        if not regex_result:
            raise InlineQueryIdNotFoundError
        regex_result = re.search(r'id"(:|: )"(\d+)"', regex_result.group(2))
        if not regex_result:
            raise InlineQueryIdNotFoundError
        return int(regex_result.group(2))
