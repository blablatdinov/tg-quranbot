# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import Final, TypedDict, final, override

from app_types.update import Update

STR_LITERAL: Final = 'str'
ASDICT_LITERAL: Final = 'asdict'


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
        self._cache: _CacheDict = {  # noqa: PEO101
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
