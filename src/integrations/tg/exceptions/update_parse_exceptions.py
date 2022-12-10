from exceptions.base_exception import BaseAppError


class MessageTextNotFoundError(BaseAppError):
    """Текст сообщения не найден."""


class CoordinatesNotFoundError(BaseAppError):
    """Координаты не найдены."""


class CallbackQueryNotFoundError(BaseAppError):
    """Информация с кнопки не найдена."""


class MessageIdNotFoundError(BaseAppError):
    """Идентификатор сообщеня не найден."""


class InlineQueryNotFoundError(BaseAppError):
    """Ошибка при отсутствии данных для поиска города."""


class InlineQueryIdNotFoundError(BaseAppError):
    """Ошибка при отсутствии данных для поиска города."""
