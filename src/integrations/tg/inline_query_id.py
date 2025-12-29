# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import SupportsInt, final, override

import attrs

from app_types.update import Update
from integrations.tg.exceptions.update_parse_exceptions import InlineQueryNotFoundError
from services.err_redirect_json_path import ErrRedirectJsonPath
from services.json_path_value import JsonPathValue


@final
@attrs.define(frozen=True)
class InlineQueryId(SupportsInt):
    """Идентификатор инлайн поиска."""

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
                    '$..inline_query.id',
                ),
                InlineQueryNotFoundError(),
            ).evaluate(),
        )
