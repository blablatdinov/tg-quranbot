from exceptions.base_exception import BaseAppError


class NotFoundReferrerIdError(BaseAppError):
    """Исключение возбуждается в случае если невозможно зарегистрировать пользователя с рефералом."""

    user_message = 'Невозможно зарегистрировать пользователя с рефералом'


class UserNotFoundError(BaseAppError):
    """Исключение возбуждается в случае если пользователь не найден."""

    user_message = 'Пользователь не найден'


class UserHasNotGeneratedPrayersError(BaseAppError):
    """У пользователя нет сгенерированных времен намаза на текущий день."""

    admin_message = ''


class NotProcessableUpdateError(BaseAppError):
    """Исключение, вызываемое если бот не знает как обработать запрос."""

    admin_message = ''


class TelegramIntegrationsError(BaseAppError):
    """Исключение, возбуждаемое при некорректном ответе от API телеграмма."""

    admin_message = 'Ошибка интеграции telegram'

    def __init__(self, message: str, chat_id: int):
        self._message = message
        self._chat_id = chat_id

    def __str__(self):
        return self._message

    def chat_id(self) -> int:
        """Получить идентификатор чата.

        :return: int
        """
        return self._chat_id


class MessageTextNotFoundException(BaseAppError):
    """Текст сообщения не найден."""
