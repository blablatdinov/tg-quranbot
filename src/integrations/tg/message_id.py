# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import SupportsInt, TypeAlias, final, override

import attrs

from app_types.update import Update
from integrations.tg.exceptions.update_parse_exceptions import MessageIdNotFoundError
from services.err_redirect_json_path import ErrRedirectJsonPath
from services.json_path_value import JsonPathValue

MessageId: TypeAlias = SupportsInt


@final
@attrs.define(frozen=True)
class TgMessageId(MessageId):
    """Идентификатор сообщения."""

    _update: Update

    @override
    def __int__(self) -> int:
        """Числовое представление.

        :return: int
        """
        return int(
            ErrRedirectJsonPath(
                JsonPathValue(
                    self._update.asdict(),
                    '$..message.message_id',
                ),
                MessageIdNotFoundError(),
            ).evaluate(),
        )
