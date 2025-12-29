# SPDX-FileCopyrightText: Copyright (c) 2018-2025 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import SupportsInt, final, override

import attrs
import httpx

from integrations.tg.udpates_url_interface import UpdatesURLInterface


@final
@attrs.define(frozen=True)
class UpdatesLongPollingURL(UpdatesURLInterface):
    """URL обновлений с таймаутом."""

    _origin: UpdatesURLInterface
    _long_polling_timeout: SupportsInt

    @override
    def generate(self, update_id: int) -> str:
        """Генерация.

        :param update_id: int
        :return: str
        """
        return str(httpx.URL(self._origin.generate(update_id)).copy_add_param(
            'timeout',
            int(self._long_polling_timeout),
        ))
