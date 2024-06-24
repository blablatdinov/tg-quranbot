from typing import final, override

import attrs
from pyeo import elegant

from srv.users.pg_user import User


@final
@attrs.define(frozen=True)
@elegant
class FkUser(User):
    """Фейковый пользователь."""

    _chat_id: int
    _day: int
    _is_active: bool

    @override
    async def chat_id(self) -> int:
        """Идентификатор чата.

        :return: int
        """
        return self._chat_id

    @override
    async def day(self) -> int:
        """День для рассылки утреннего контента.

        :return: int
        """
        return self._day

    @override
    async def is_active(self) -> bool:
        """Статус пользователя.

        :return: bool
        """
        return self._is_active
