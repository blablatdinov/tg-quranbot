from app_types.update import Update
from handlers.PrayerNames import PrayerNames
from integrations.tg.keyboard import Keyboard


import attrs
import ujson
from pyeo import elegant


from typing import final


@final
@attrs.define(frozen=True)
@elegant
class SkippedPrayersKeyboard(Keyboard):
    """Клавиатура для пропущеных намазов."""

    async def generate(self, update: Update) -> str:
        """Генерация клавиатуры.

        :param update: Update
        :return: str
        """
        return ujson.dumps({
            'inline_keyboard': [
                [{
                    'text': '{0}: (-1)'.format(field.value[1]),
                    'callback_data': 'decr({0})'.format(field.name),
                }]
                for field in PrayerNames.fields_without_sunrise()
            ],
        })