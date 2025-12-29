# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final, override

import attrs

from app_types.stringable import SupportsStr


@final
@attrs.define(frozen=True)
class UpdatesURL(SupportsStr):
    """Базовый URL обновлений из телеграма."""

    _token: str

    @override
    def __str__(self) -> str:
        """Строчное представление.

        :return: str
        """
        return 'https://api.telegram.org/bot{0}/getUpdates'.format(self._token)
