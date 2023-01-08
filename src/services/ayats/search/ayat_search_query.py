"""The MIT License (MIT).

Copyright (c) 2018-2023 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
OR OTHER DEALINGS IN THE SOFTWARE.
"""
from typing import Protocol, final

from exceptions.content_exceptions import AyatNotFoundError, SuraNotFoundError


class SearchQueryInterface(Protocol):
    """Интерфейс объекта с запросом для поиска."""

    def sura(self) -> int:
        """Номер суры."""

    def ayat(self) -> str:
        """Номер аята."""


@final
class SearchQuery(SearchQueryInterface):
    """Запросом для поиска."""

    def __init__(self, query: str):
        """Конструктор класса.

        :param query: str
        """
        self._query = query

    def sura(self) -> int:
        """Номер суры.

        :return: int
        """
        return int(self._query.split(':')[0])

    def ayat(self) -> str:
        """Номер аята.

        :return: str
        """
        return self._query.split(':')[1]


@final
class ValidatedSearchQuery(SearchQueryInterface):
    """Декоратор, валидирующий запрос для поиска."""

    def __init__(self, query: SearchQueryInterface):
        """Конструктор класса.

        :param query: SearchQueryInterface
        """
        self._origin = query

    def sura(self) -> int:
        """Номер суры.

        :return: int
        :raises SuraNotFoundError: if sura not found
        """
        max_sura_num = 114
        sura_num = self._origin.sura()
        if not 0 < sura_num <= max_sura_num:  # noqa: WPS508
            # https://github.com/wemake-services/wemake-python-styleguide/issues/1942
            raise SuraNotFoundError
        return sura_num

    def ayat(self) -> str:
        """Номер аята.

        :return: str
        :raises AyatNotFoundError: if ayat not found
        """
        ayat_num = self._origin.ayat()
        if ayat_num == '0' or '-' in ayat_num:
            raise AyatNotFoundError
        return ayat_num
