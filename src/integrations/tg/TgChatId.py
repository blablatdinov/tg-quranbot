from typing import final, override

import attrs
from pyeo import elegant

from app_types.update import Update
from exceptions.base_exception import InternalBotError
from integrations.tg.fk_chat_id import ChatId
from services.ErrRedirectJsonPath import ErrRedirectJsonPath
from services.MatchManyJsonPath import MatchManyJsonPath


@final
@attrs.define(frozen=True)
@elegant
class TgChatId(ChatId):
    """Идентификатор чата."""

    _update: Update

    @override
    def __int__(self) -> int:
        """Числовое представление.

        :return: int
        """
        return int(
            ErrRedirectJsonPath(
                MatchManyJsonPath(
                    self._update.asdict(),
                    ('$..chat.id', '$..from.id'),
                ),
                InternalBotError(),
            ).evaluate(),
        )
