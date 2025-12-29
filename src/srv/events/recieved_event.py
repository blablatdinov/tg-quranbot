# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import Protocol, TypeAlias, TypeVar

from eljson.json import Json

JsonPathQuery: TypeAlias = str
JsonPathReturnType_co = TypeVar('JsonPathReturnType_co', covariant=True)


class ReceivedEvent(Protocol[JsonPathReturnType_co]):
    """Событие."""

    async def process(self, json_doc: Json) -> None:
        """Обработать событие.

        :param json_doc: Json
        """
