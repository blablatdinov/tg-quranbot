# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import TypeAlias, final, override

import attrs
from eljson.json import Json
from sqlalchemy.ext.asyncio import AsyncEngine

from srv.ayats.pg_ayat import PgAyat
from srv.events.recieved_event import ReceivedEvent

JsonPathQuery: TypeAlias = str
AyatChangedEvent: TypeAlias = ReceivedEvent


@final
@attrs.define(frozen=True)
class RbmqAyatChangedEvent(AyatChangedEvent):
    """Событие изменения аята из rabbitmq."""

    _pgsql: AsyncEngine

    @override
    async def process(self, json_doc: Json) -> None:  # type: ignore[override]
        """Обработка события.

        :param json_doc: Json
        """
        pg_ayat = PgAyat.ayat_changed_event_ctor(json_doc, self._pgsql)
        await pg_ayat.change(json_doc)
