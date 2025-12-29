# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final, override

import attrs

from app_types.stringable import SupportsStr
from integrations.tg.udpates_url_interface import UpdatesURLInterface


@final
@attrs.define(frozen=True)
class UpdatesWithOffsetURL(UpdatesURLInterface):
    """URL для получения только новых обновлений."""

    _updates_url: SupportsStr

    @override
    def generate(self, update_id: int) -> str:
        """Генерация.

        :param update_id: int
        :return: str
        """
        return '{0}?offset={1}'.format(self._updates_url, update_id)
