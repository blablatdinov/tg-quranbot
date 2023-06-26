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
import json
from typing import final

from attrs import define

from app_types.stringable import Stringable
from app_types.update import Update
from integrations.tg.update_struct import UpdateStruct
from services.weak_cache import weak_lru


@final
@define
class TgUpdate(Update):
    """Объект обновления от телеграмма.

    _raw_udpate: Stringable - сырая json строка
    """

    _raw_update: Stringable

    def __str__(self) -> str:
        """Приведение к строке.

        :return: str
        """
        return str(self._raw_update)

    def parsed(self) -> UpdateStruct:
        """Десериализованный объект.

        :return: UpdateStruct
        """
        return UpdateStruct.parse_raw(str(self))

    def dict(self) -> dict:
        """Словарь.

        TODO: возможно стоит возвращать валидированный dict:
            return self.parsed().dict()

        :return: dict
        """
        return json.loads(str(self._raw_update))


@final
@define
class CachedTgUpdate(Update):
    """Декоратор, для избежания повторной десериализации.

    _origin: Update - оригинальный объект обновления
    """

    _origin: Update

    @weak_lru()
    def __str__(self):
        """Приведение к строке.

        :return: str
        """
        return self._origin.__str__()

    @weak_lru()
    def parsed(self) -> UpdateStruct:
        """Десериализованный объект.

        :return: UpdateStruct
        """
        return self._origin.parsed()

    @weak_lru()
    def dict(self) -> dict:
        """Словарь.

        :return: dict
        """
        return self._origin.dict()

    def __hash__(self):
        """Хэш объекта.

        :return: Something
        """
        return str(self._origin).__hash__()
