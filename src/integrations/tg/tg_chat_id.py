# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final, override

import attrs

from app_types.update import Update
from exceptions.base_exception import InternalBotError
from integrations.tg.fk_chat_id import ChatId
from services.err_redirect_json_path import ErrRedirectJsonPath
from services.match_many_json_path import MatchManyJsonPath


@final
@attrs.define(frozen=True)
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
