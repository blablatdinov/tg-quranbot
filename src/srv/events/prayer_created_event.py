# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

import datetime
from typing import final, override

import attrs
import pytz
from databases import Database
from eljson.json import Json
from loguru import logger

from srv.events.recieved_event import ReceivedEvent


@final
@attrs.define(frozen=True)
class PrayerCreatedEvent(ReceivedEvent):
    """Событие создания аята из rabbitmq."""

    _pgsql: Database

    @override
    async def process(self, json: Json) -> None:
        """Обработка события.

        :param json: Json
        """
        query = '\n'.join([
            'INSERT INTO prayers (name, time, city_id, day) VALUES',
            '(:name, :time, :city_id, :day)',
        ])
        await self._pgsql.execute(
            query,
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
        logger.info('Prayer created')
