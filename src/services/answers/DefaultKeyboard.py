from typing import final, override

from pyeo import elegant

from app_types.update import Update
from integrations.tg.keyboard import Keyboard


@final
@elegant
class DefaultKeyboard(Keyboard):
    """Класс клавиатуры по умолчанию."""

    @override
    async def generate(self, update: Update) -> str:
        """Генерация.

        :param update: Update
        :return: str
        """
        return '{"keyboard":[["🎧 Подкасты"],["🕋 Время намаза","🏘️ Поменять город"],["🌟 Избранное","🔍 Найти аят"]]}'
