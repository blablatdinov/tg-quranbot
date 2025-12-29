# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final, override

import attrs

from app_types.update import Update
from integrations.tg.tg_chat_id import TgChatId
from services.debug_param import DebugParam


@final
@attrs.frozen
class ChatIdDebugParam(DebugParam):
    """Отладочная информация с идентификатором чата."""

    @override
    async def debug_value(self, update: Update) -> str:
        """Идентификатор чата.

        :param update: Update
        :return: str
        """
        return 'Chat id: {0}'.format(int(TgChatId(update)))
