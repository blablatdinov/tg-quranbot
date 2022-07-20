from aiogram import types


class UserPrayerStatusInterface(object):
    """Интерфейс для работы со статусом прочитанности намаза у польозвателя."""

    async def change(self, is_readed: bool):
        """Метод меняет статус прочитанности намаза.

        :param is_readed: bool
        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError

    async def generate_refresh_keyboard(self) -> types.InlineKeyboardMarkup:
        """Сгенерировать обновленную клавиатуру.

        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError
