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
from asyncpg import UniqueViolationError
from databases import Database
from loguru import logger
from pyeo import elegant

from app_types.intable import AsyncIntable
from exceptions.base_exception import InternalBotError
from exceptions.user import UserAlreadyExists
from integrations.tg.chat_id import TgChatId
from services.start.start_message import AsyncIntOrNone


@elegant
class NewUser(Protocol):

    async def create(self): ...


@final
@attrs.define(frozen=True)
@elegant
class PgNewUser(NewUser):

    _referrer_chat_id: AsyncIntOrNone
    _new_user_chat_id: TgChatId
    _pgsql: Database

    async def create(self) -> None:
        chat_id = int(self._new_user_chat_id)
        logger.debug('Insert in DB User <{0}>...'.format(chat_id))
        query = """
            INSERT INTO
            users (chat_id, referrer_id, day)
            VALUES (:chat_id, :referrer_id, 2)
            RETURNING (chat_id, referrer_id)
        """
        try:
            await self._pgsql.fetch_one(
                query,
                {'chat_id': chat_id, 'referrer_id': await self._referrer_chat_id.to_int()},
            )
        except UniqueViolationError:
            raise UserAlreadyExists
        logger.debug('User <{0}> inserted in DB'.format(chat_id))
