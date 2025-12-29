# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final, override

import attrs
import httpx

from app_types.supports_bool import SupportsBool
from app_types.update import Update
from integrations.tg.tg_answers import TgAnswer
from srv.files.tg_file_id_not_filled_safe_answer import TgFileIdNotFilledSafeAnswer


@final
@attrs.define(frozen=True)
class FileAnswer(TgAnswer):
    """Класс ответа с файлом."""

    _telegram_file_id_answer: TgAnswer
    _file_link_answer: TgAnswer
    _debug_mode: SupportsBool

    @override
    async def build(self, update: Update) -> list[httpx.Request]:
        """Отправка.

        :param update: Update
        :return: list[httpx.Request]
        """
        if self._debug_mode:
            return await self._file_link_answer.build(update)
        return await TgFileIdNotFilledSafeAnswer(
            self._telegram_file_id_answer,
            self._file_link_answer,
        ).build(update)
