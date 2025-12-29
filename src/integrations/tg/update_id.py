# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import SupportsInt, final, override

import attrs

from app_types.update import Update
from exceptions.base_exception import InternalBotError
from services.err_redirect_json_path import ErrRedirectJsonPath
from services.json_path_value import JsonPathValue


@final
@attrs.define(frozen=True)
class UpdateId(SupportsInt):
    """Идентификатор обновления."""

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
                    '$..update_id',
                ),
                InternalBotError(),
            ).evaluate(),
        )
