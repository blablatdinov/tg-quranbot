class BaseAppError(Exception):
    """Базовое исключение бота."""


class InternalBotError(BaseAppError):
    """Внутренняя ошибка бота."""

    user_message = ''
