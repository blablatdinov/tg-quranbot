# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final, override

import attrs

from integrations.tg.udpates_url_interface import UpdatesURLInterface


@final
@attrs.define(frozen=True)
class FkUpdatesURL(UpdatesURLInterface):
    """Fake updates url."""

    _origin: str

    @override
    def generate(self, update_id: int) -> str:
        """Генерация.

        :param update_id: int
        """
        return self._origin
