import re

from exceptions import BaseAppError
from app_types.intable import Intable


class RegularExpression(Intable):

    _text_for_searching: str
    _pattern: str

    def __init__(self, text_for_searching: str, pattern: str):
        self._text_for_searching = text_for_searching
        self._pattern = pattern

    def to_int(self) -> int:
        regex_result = re.search(self._pattern, self._text_for_searching)
        if not regex_result:
            raise BaseAppError
        finded = regex_result.group(0)
        return int(finded)
