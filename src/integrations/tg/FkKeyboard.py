from app_types.update import Update
from integrations.tg.keyboard import Keyboard


import attrs
from pyeo import elegant


from typing import final, override


@elegant
@final
@attrs.define(frozen=True)
class FkKeyboard(Keyboard):
    """Фейковая клавиатура."""

    @override
    async def generate(self, update: Update) -> str:
        """Генерация.

        :param update: Update
        :return: str
        """
        return '{}'  # noqa: P103 it is empty json