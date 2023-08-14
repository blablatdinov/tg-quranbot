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

import attrs
from pyeo import elegant

from app_types.stringable import SupportsStr
from integrations.tg.update_struct import UpdateStruct


@elegant
class Update(SupportsStr, Protocol):
    """Интерфейс объектов, которые можно привести к строке."""

    def __str__(self) -> str:
        """Приведение к строке."""

    def parsed(self) -> UpdateStruct:
        """Десериализованный объект."""

    def dict(self) -> dict:
        """Словарь."""


@final
@attrs.define(frozen=True)
@elegant
class FkUpdate(Update):
    """Подделка обновления."""

    _raw: SupportsStr | None = ''

    def __str__(self):
        """Приведение к строке.

        :return: str
        """
        return self._raw

    def parsed(self) -> UpdateStruct:
        """Десериализованный объект.

        :return: UpdateStruct
        """
        return UpdateStruct(ok=True)

    def dict(self):
        """Словарь.

        :return: dict
        """
        return {}
