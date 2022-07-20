from aiogram import types


class AyatSearchKeyboardInterface(object):
    """Интерфейс для клавиатур."""

    async def generate(self) -> types.InlineKeyboardMarkup:
        """Сгенерировать клавиатуру.

        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError
