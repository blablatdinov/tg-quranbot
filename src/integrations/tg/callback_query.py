# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final, override

import attrs

from app_types.stringable import SupportsStr
from app_types.update import Update
from integrations.tg.exceptions.update_parse_exceptions import CallbackQueryNotFoundError
from services.err_redirect_json_path import ErrRedirectJsonPath
from services.json_path_value import JsonPathValue


@final
@attrs.define(frozen=True)
class CallbackQueryData(SupportsStr):
    """Информация с кнопки."""

    _update: Update

    @override
    def __str__(self) -> str:
        """Строковое представление.

        :return: str
        """
        return str(
            ErrRedirectJsonPath(
                JsonPathValue(
                    self._update.asdict(),
                    '$..callback_query.data',
                ),
                CallbackQueryNotFoundError(),
            ).evaluate(),
        )
