from aiogram import types

from services.answers.answer import KeyboardInterface


class CitySearchKeyboard(KeyboardInterface):
    """Клавиатура с поиском города."""

    async def generate(self):
        """Генерация.

        :return: types.InlineKeyboardMarkup()
        """
        return types.InlineKeyboardMarkup().row(
            types.InlineKeyboardButton('Поиск города', switch_inline_query_current_chat=''),
        )
