# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final, override

import attrs
from asyncpg import ForeignKeyViolationError, UniqueViolationError
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from app_types.async_int_or_none import AsyncIntOrNone
from app_types.fk_async_int_or_none import FkAsyncIntOrNone
from app_types.logger import LogSink
from exceptions.internal_exceptions import UserNotFoundError
from exceptions.user import UserAlreadyExistsError
from integrations.tg.fk_chat_id import ChatId
from srv.users.new_user import NewUser


@final
@attrs.define(frozen=True)
class PgNewUser(NewUser):
    """Новый пользователь в БД postgres."""

    _referrer_chat_id: AsyncIntOrNone
    _new_user_chat_id: ChatId
    _pgsql: AsyncEngine
    _logger: LogSink

    @classmethod
    def ctor(cls, new_user_chat_id: ChatId, pgsql: AsyncEngine, logger: LogSink) -> NewUser:
        """Конструктор без реферера.

        :param new_user_chat_id: ChatId
        :param pgsql: AsyncEngine
        :param logger: LogSink
        :return: NewUser
        """
        return cls(
            FkAsyncIntOrNone(None),
            new_user_chat_id,
            pgsql,
            logger,
        )

    @override
    async def create(self) -> None:
        """Создание.

        :raises UserAlreadyExistsError: пользователь уже зарегистрирован
        :raises UserNotFoundError: не найден реферер
        """
        chat_id = int(self._new_user_chat_id)
        self._logger.debug('Insert in DB User <{0}>...'.format(chat_id))
        query = '\n'.join([
            'INSERT INTO',
            'users (chat_id, referrer_id, day, is_active)',
            'VALUES (:chat_id, :referrer_id, 2, true)',
            'RETURNING (chat_id, referrer_id)',
        ])
        try:
            async with self._pgsql.connect() as conn:
                await conn.execute(
                    text(query),
                    {'chat_id': chat_id, 'referrer_id': await self._referrer_chat_id.to_int()},
                )
                await conn.commit()
        except UniqueViolationError as err:
            raise UserAlreadyExistsError from err
        except ForeignKeyViolationError as err:
            raise UserNotFoundError from err
        self._logger.debug('User <{0}> inserted in DB'.format(chat_id))
