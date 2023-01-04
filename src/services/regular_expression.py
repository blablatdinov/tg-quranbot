import re

from app_types.intable import Intable
from exceptions.base_exception import BaseAppError


class IntableRegularExpression(Intable):
    """Регулярное выражение, которое можно привести к числу."""

    def __init__(self, text_for_searching: str):
        """Конструктор класса.

        :param text_for_searching: str
        """
        self._text_for_searching = text_for_searching

    def __int__(self) -> int:
        """Приведение к числу.

        :returns: int
        :raises BaseAppError: если не удалось получить результат по регулярному выражению
        """
        regex_result = re.search(r'\d+', self._text_for_searching)
        if not regex_result:
            raise BaseAppError
        finded = regex_result.group(0)
        return int(finded)
