from app_types.fk_async_int import FkAsyncInt
from app_types.intable import AsyncInt
from exceptions.base_exception import BaseAppError
from exceptions.user import StartMessageNotContainReferrerError
from services.regular_expression import IntableRegularExpression
from srv.users.PgUser import PgUser
from srv.users.PgValidChatId import PgValidChatId


import attrs
from databases import Database
from pyeo import elegant


from typing import final, override


@final
@attrs.define(frozen=True)
@elegant
class ReferrerChatId(AsyncInt):
    """Идентификатор чата пригласившего."""

    _message: str
    _pgsql: Database

    @override
    async def to_int(self) -> int:
        """Получить идентификатор пригласившего.

        :return: int
        :raises StartMessageNotContainReferrerError: if message not contain referrer id
        """
        try:
            message_meta = int(IntableRegularExpression(self._message))
        except BaseAppError as err:
            raise StartMessageNotContainReferrerError from err
        max_legacy_id = 3000
        if message_meta < max_legacy_id:
            return await PgUser.legacy_id_ctor(
                FkAsyncInt(
                    IntableRegularExpression(self._message),
                ),
                self._pgsql,
            ).chat_id()
        return await PgUser(
            PgValidChatId.int_ctor(
                self._pgsql,
                IntableRegularExpression(self._message),
            ),
            self._pgsql,
        ).chat_id()