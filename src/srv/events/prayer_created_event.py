# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

import datetime
from typing import final, override

import attrs
import pytz
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from srv.events.recieved_event import ReceivedEvent


@final
@attrs.define(frozen=True)
class PrayerCreatedEvent(ReceivedEvent):
    """Событие создания аята из rabbitmq."""

    _pgsql: AsyncEngine

    @override
    async def process(self, json: Json) -> None:  # type: ignore[override]
        """Обработка события.

        :param json: Json
        """
        query = '\n'.join([
            'INSERT INTO prayers (name, time, city_id, day) VALUES',
            '(:name, :time, :city_id, :day)',
        ])
        async with self._pgsql.connect() as conn:
            await conn.execute(
                text(query),
                {
                    'name': json.path('$.data.name')[0],
                    'time': datetime.datetime.strptime(json.path('$.data.time')[0], '%H:%M').replace(
                        tzinfo=pytz.timezone('Europe/Moscow'),
                    ),
                    'city_id': json.path('$.data.city_id')[0],
                    'day': datetime.datetime.strptime(json.path('$.data.day')[0], '%Y-%m-%d').astimezone(
                        pytz.timezone('Europe/Moscow'),
                    ),
                },
            )
            await conn.commit()
        logger.info('Prayer created')


from eljson.json import Json
from loguru import logger
