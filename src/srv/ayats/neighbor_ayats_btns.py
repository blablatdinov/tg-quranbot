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

from contextlib import suppress
from typing import final, override

import attrs

from exceptions.content_exceptions import AyatNotFoundError
from srv.ayats.ayat_callback_template_enum import AyatCallbackTemplateEnum
from srv.ayats.neighbor_ayats import NeighborAyats
from srv.ayats.neighbor_ayats_buttons import NeighborAyatsButtons


@final
@attrs.define(frozen=True)
class NeighborAyatsBtns(NeighborAyatsButtons):
    """Кнопки для клавиатуры с соседними аятами."""

    _ayats_neighbors: NeighborAyats
    _callback_template: AyatCallbackTemplateEnum

    @override
    async def left(self) -> dict[str, str] | None:
        """Левая кнопка.

        :return: dict[str, str] | None
        """
        with suppress(AyatNotFoundError):
            left = await self._ayats_neighbors.left_neighbor()
            return {
                'text': '<- {0}:{1}'.format(
                    await left.identifier().sura_num(),
                    await left.identifier().ayat_num(),
                ),
                'callback_data': self._callback_template.format(await left.identifier().ayat_id()),
            }
        return None

    @override
    async def right(self) -> dict[str, str] | None:
        """Правая кнопка.

        :return: dict[str, str] | None
        """
        with suppress(AyatNotFoundError):
            right = await self._ayats_neighbors.right_neighbor()
            return {
                'text': '{0}:{1} ->'.format(
                    await right.identifier().sura_num(),
                    await right.identifier().ayat_num(),
                ),
                'callback_data': self._callback_template.format(await right.identifier().ayat_id()),
            }
        return None
