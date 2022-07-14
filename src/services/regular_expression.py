import re

from app_types.intable import Intable
from exceptions import BaseAppError


class RegularExpression(Intable):

    _pattern: str
    _text_for_searching: str

    def __init__(self, pattern: str, text_for_searching: str):
        self._pattern = pattern
        self._text_for_searching = text_for_searching

    def to_int(self) -> int:
        regex_result = re.search(self._pattern, self._text_for_searching)
        if not regex_result:
            raise BaseAppError
        finded = regex_result.group(0)
        return int(finded)
