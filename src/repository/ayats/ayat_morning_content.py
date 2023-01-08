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
from typing import final
from typing import Protocol

from databases import Database
from pydantic import BaseModel, parse_obj_as


class ContentSpam(BaseModel):
    """Модель для рассылки утреннего контента."""

    chat_id: int
    content: str  # noqa: WPS110
    link: str


class AyatMorningContentRepositoryInterface(Protocol):
    """Интерфейс для работы с хранилищем данных для рассылок."""

    async def get_morning_content(self) -> list[ContentSpam]:
        """Получить контент для рассылки."""


class AyatMorningContentRepository(AyatMorningContentRepositoryInterface):
    """Класс для работы с хранилищем данных для рассылок."""

    def __init__(self, connection: Database):
        """Конструктор класса.

        :param connection: Database
        """
        self._connection = connection

    async def get_morning_content(self) -> list[ContentSpam]:
        """Получить контент для рассылки.

        :returns: list[ContentSpam]
        """
        query = """
            SELECT
                s.chat_id,
                STRING_AGG(
                    '<b>' || sura.sura_id::CHARACTER VARYING || ': ' || a.ayat_number || ')</b> ' || a .content || '\n',
                    ''
                    ORDER BY a.ayat_id
                ) AS content,
                STRING_AGG(sura.link, '|' ORDER BY a.ayat_id) AS link
            FROM users AS s
            LEFT JOIN ayats AS a ON a.day=s.day
            LEFT JOIN suras AS sura ON a.sura_id=sura.sura_id
            WHERE s.is_active = 't'
            GROUP BY s.chat_id
        """
        rows = await self._connection.fetch_all(query)
        return parse_obj_as(list[ContentSpam], [row._mapping for row in rows])  # noqa: WPS437
