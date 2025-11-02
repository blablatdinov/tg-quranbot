# The MIT License (MIT).
#
# Copyright (c) 2018-2025 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
# OR OTHER DEALINGS IN THE SOFTWARE.

from typing import TypedDict, final, override, Final

from app_types.update import Update

STR_LITERAL: Final = 'str'
ASDICT_LITERAL: Final = 'str'


@final
class _CacheDict(TypedDict):

    str: str
    asdict: dict


@final
# object for caching
class CachedTgUpdate(Update):  # noqa: PEO200
    """Декоратор, для избежания повторной десериализации."""

    def __init__(self, origin: Update) -> None:
        """Ctor.

        :param origin: Update - оригинальный объект обновления
        """
        self._origin = origin
        self._cache: _CacheDict = {
            STR_LITERAL: '',
            ASDICT_LITERAL: {},
        }

    @override
    def __str__(self) -> str:
        """Приведение к строке.

        :return: str
        """
        if not self._cache[STR_LITERAL]:
            self._cache[STR_LITERAL] = str(self._origin)
        return self._cache[STR_LITERAL]

    @override
    def asdict(self) -> dict:
        """Словарь.

        :return: dict
        """
        if not self._cache[ASDICT_LITERAL]:
            self._cache[ASDICT_LITERAL] = self._origin.asdict()
        return self._cache[ASDICT_LITERAL]
