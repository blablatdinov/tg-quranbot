# The MIT License (MIT).
#
# Copyright (c) 2018-2025 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
# OR OTHER DEALINGS IN THE SOFTWARE.

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
