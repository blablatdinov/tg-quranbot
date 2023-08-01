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
from typing import final

import attrs
from pyeo import elegant

from app_types.intable import AsyncIntable
from exceptions.base_exception import BaseAppError
from exceptions.user import StartMessageNotContainReferrer
from repository.users.user import UserRepositoryInterface
from services.regular_expression import IntableRegularExpression


@final
@attrs.define(frozen=True)
@elegant
class SmartReferrerChatId(AsyncIntable):
    """Идентификатор чата пригласившего."""

    _message: str
    _user_repo: UserRepositoryInterface

    async def to_int(self) -> int:
        """Получить идентификатор пригласившего.

        :return: int
        :raises StartMessageNotContainReferrer: if message not contain referrer id
        """
        try:
            message_meta = int(IntableRegularExpression(self._message))
        except BaseAppError as err:
            raise StartMessageNotContainReferrer from err
        max_legacy_id = 3000
        if message_meta < max_legacy_id:
            return (await self._user_repo.get_by_id(message_meta)).chat_id
        return message_meta
