from contextlib import suppress
from typing import final

import attrs
from pyeo import elegant

from exceptions.content_exceptions import AyatNotFoundError
from srv.ayats.ayat_callback_template_enum import AyatCallbackTemplateEnum
from srv.ayats.neighbor_ayats import NeighborAyats
from srv.ayats.neighbor_ayats_buttons import NeighborAyatsButtons


@final
@attrs.define(frozen=True)
@elegant
class NeighborAyatsBtns(NeighborAyatsButtons):
    """Кнопки для клавиатуры с соседними аятами."""

    _ayats_neighbors: NeighborAyats
    _callback_template: AyatCallbackTemplateEnum

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
