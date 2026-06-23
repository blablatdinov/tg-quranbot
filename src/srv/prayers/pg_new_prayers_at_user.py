# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

import datetime
import uuid
from typing import final, override

import attrs
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncEngine

from exceptions.internal_exceptions import PrayerAtUserAlreadyExistsError, PrayerAtUserNotCreatedError
from exceptions.prayer_exceptions import PrayersNotFoundError
from integrations.tg.fk_chat_id import ChatId
from srv.prayers.new_prayers_at_user import NewPrayersAtUser


@final
@attrs.define(frozen=True)
class PgNewPrayersAtUser(NewPrayersAtUser):
    """Новые записи о статусе намаза."""

    _chat_id: ChatId
    _pgsql: AsyncEngine

    @override
    async def create(self, date: datetime.date) -> None:
        """Создать.

        :param date: datetime.date
        :raises PrayerAtUserAlreadyExistsError: у пользователя уже созданы времена намазов
        :raises PrayerAtUserNotCreatedError: не удалось создать времена намазов
        """
        prayer_group_id = str(uuid.uuid4())
        async with self._pgsql.connect() as conn:
            await conn.execute(
                text('INSERT INTO prayers_at_user_groups VALUES (:prayer_group_id)'),
                {'prayer_group_id': prayer_group_id},
            )
            await conn.commit()
        async with self._pgsql.connect() as conn:
            query_result = await conn.execute(
                text('\n'.join([
                    'SELECT COUNT(*) FROM prayers AS p',
                    'INNER JOIN cities AS c ON p.city_id = c.city_id',
                    'INNER JOIN users AS u ON u.city_id = c.city_id',
                    'WHERE u.chat_id = :chat_id',
                    '  AND p.day = :date',
                ])),
                {'chat_id': int(self._chat_id), 'date': date},
            )
            row = query_result.fetchone()
        exists_prayers = row[0] if row else 0
        if not exists_prayers:
            async with self._pgsql.connect() as conn:
                query_result = await conn.execute(
                    text('\n'.join([
                        'SELECT c.name FROM users AS u',
                        'INNER JOIN cities AS c ON u.city_id = c.city_id',
                        'WHERE u.chat_id = :chat_id',
                    ])),
                    {'chat_id': int(self._chat_id)},
                )
                row = query_result.fetchone()
            city_name = row[0] if row else None
            raise PrayersNotFoundError(str(city_name) if city_name else '', date)
        query = '\n'.join([
            'INSERT INTO prayers_at_user',
            '(user_id, prayer_id, is_read, prayer_group_id)',
            '  SELECT',
            '    :chat_id,',
            '    p.prayer_id,',
            '    false,',
            '    :prayer_group_id',
            '  FROM prayers AS p',
            '  INNER JOIN cities AS c ON p.city_id = c.city_id',
            '  INNER JOIN users AS u ON u.city_id = c.city_id',
            "  WHERE p.day = :date AND u.chat_id = :chat_id AND p.name <> 'sunrise'",
            '  ORDER BY',
            "    ARRAY_POSITION(ARRAY['fajr', 'dhuhr', 'asr', 'maghrib', 'isha''a']::text[], p.name::text)",
            '  RETURNING *',
        ])
        try:
            async with self._pgsql.connect() as conn:
                query_result = await conn.execute(text(query), {
                    'chat_id': int(self._chat_id),
                    'prayer_group_id': prayer_group_id,
                    'date': date,
                })
                rows = query_result.fetchall()
                await conn.commit()
        except IntegrityError as err:
            if 'duplicate key value violates unique constraint' in str(err):
                raise PrayerAtUserAlreadyExistsError from err
        if not rows:
            raise PrayerAtUserNotCreatedError
