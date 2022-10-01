import json
from contextlib import suppress

from exceptions.content_exceptions import AyatNotFoundError
from integrations.tg.tg_answers.update import Update
from repository.ayats.neighbor_ayats import NeighborAyatsRepositoryInterface
from services.answers.answer import KeyboardInterface
from services.ayats.ayat_keyboard_callback_template import AyatCallbackTemplate


class NeighborAyatKeyboard(KeyboardInterface):
    """Клавиатура с соседними аятами."""

    def __init__(self, ayats_neighbors: NeighborAyatsRepositoryInterface, callback_template: AyatCallbackTemplate):
        self._ayats_neighbors = ayats_neighbors
        self._callback_template = callback_template

    async def generate(self, update: Update) -> str:
        """Генерация клавиатуры.

        :param update: Update
        :return: str
        """
        buttons = []
        with suppress(AyatNotFoundError):
            left = await self._ayats_neighbors.left_neighbor()
            buttons.append({
                'text': '<- {0}:{1}'.format(left.sura_num, left.ayat_num),
                'callback_data': self._callback_template.format(left.id),
            })
        with suppress(AyatNotFoundError):
            print('Try get right neighbor')
            right = await self._ayats_neighbors.right_neighbor()
            buttons.append({
                'text': '{0}:{1} ->'.format(right.sura_num, right.ayat_num),
                'callback_data': self._callback_template.format(right.id),
            })
        print(f'{buttons=}')
        return json.dumps({
            'inline_keyboard': [buttons],
        })
