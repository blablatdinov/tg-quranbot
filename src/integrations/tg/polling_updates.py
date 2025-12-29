# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import SupportsInt, final, override

import attrs
import httpx
import ujson

from app_types.update import Update
from integrations.tg.udpates_url_interface import UpdatesURLInterface
from integrations.tg.update import TgUpdate
from integrations.tg.updates_iterator import UpdatesIterator


@final
@attrs.define()
class PollingUpdatesIterator(UpdatesIterator):  # noqa: PEO200. It is generator with mutable offset
    """Итератор по обновлениям."""

    _updates_url: UpdatesURLInterface
    _updates_timeout: SupportsInt

    _offset: int = 0

    @override
    def __aiter__(self) -> UpdatesIterator:
        """Точка входа в итератор.

        :return: UpdatesIteratorInterface
        """
        return self

    @override
    async def __anext__(self) -> list[Update]:
        """Вернуть следующий элемент.

        :return: list[Update]
        """
        async with httpx.AsyncClient(timeout=5) as client:
            try:
                resp = await client.get(
                    self._updates_url.generate(self._offset),
                    timeout=int(self._updates_timeout),
                )
            except (httpx.ReadTimeout, httpx.ConnectTimeout):
                return []
            resp_content = resp.text
            try:
                parsed_result = ujson.loads(resp_content)['result']
            except KeyError:
                return []
            if not parsed_result:
                return []
            self._offset = parsed_result[-1]['update_id'] + 1  # noqa: WPS601
            return [TgUpdate(elem) for elem in parsed_result]
