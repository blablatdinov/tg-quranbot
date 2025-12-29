# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

import uuid
from typing import final, override

import attrs

from srv.prayers.city import City


@final
@attrs.define(frozen=True)
class FkCity(City):
    """Стаб города."""

    _city_id: uuid.UUID
    _name: str

    @classmethod
    def name_ctor(cls, name: str) -> City:
        """Конструктор с генерацией uuid."""
        return cls(uuid.uuid4(), name)  # noqa: PEO102

    @override
    async def city_id(self) -> uuid.UUID:
        """Идентификатор города.

        :return: uuid.UUID
        """
        return self._city_id

    @override
    async def name(self) -> str:
        """Имя города.

        :return: name
        """
        return self._name
