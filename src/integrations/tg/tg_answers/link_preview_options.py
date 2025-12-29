# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final, override

import attrs
import httpx
import ujson
from furl import furl

from app_types.update import Update
from integrations.tg.tg_answers.tg_answer import TgAnswer


@final
@attrs.define(frozen=True)
class TgLinkPreviewOptions(TgAnswer):
    """Опции превью ссылок."""

    _origin: TgAnswer
    _disabled: bool

    @override
    async def build(self, update: Update) -> list[httpx.Request]:
        """Формирование запросов.

        :param update: Update
        :return: list[httpx.Request]
        """
        return [
            httpx.Request(
                request.method,
                furl(request.url).add({
                    'link_preview_options': ujson.dumps({'is_disabled': self._disabled}),
                }).url,
            )
            for request in await self._origin.build(update)
        ]
