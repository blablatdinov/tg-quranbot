from aiogram import types


def get_default_markup() -> types.ReplyKeyboardMarkup:
    """Получить дефолтную клавиатуру.

    :returns: Keyboard
    """
    return (
        types.ReplyKeyboardMarkup()
        .row(types.KeyboardButton('🎧 Подкасты'))
        .row(types.KeyboardButton('🕋 Время намаза'))
        .row(types.KeyboardButton('🌟 Избранное'), types.KeyboardButton('🔍 Найти аят'))
    )
