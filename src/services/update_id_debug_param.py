# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final, override

import attrs

from app_types.update import Update
from integrations.tg.update_id import UpdateId
from services.debug_param import DebugParam


@final
@attrs.define(frozen=True)
class UpdateIdDebugParam(DebugParam):
    """Отладочная информация с идентификатором обновления."""

    @override
    async def debug_value(self, update: Update) -> str:
        """Идентификатор обновления.

        :param update: Update
        :return: str
        """
        return 'Update id: {0}'.format(int(UpdateId(update)))
