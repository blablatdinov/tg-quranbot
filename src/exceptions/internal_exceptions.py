from exceptions.base_exception import BaseAppError


class NotFoundReferrerIdError(BaseAppError):
    """Исключение возбуждается в случае если невозможно зарегистрировать пользователя с рефералом."""

    user_message = 'Невозможно зарегистрировать пользователя с рефералом'


class UserNotFoundError(BaseAppError):
    """Исключение возбуждается в случае если пользователь не найден."""

    user_message = 'Пользователь не найден'


class TelegramIntegrationsError(BaseAppError):
    """Исключение, возбуждаемое при некорректном ответе от API телеграмма."""

    admin_message = 'Ошибка интеграции telegram'


class UserHasNotGeneratedPrayersError(BaseAppError):
    """У пользователя нет сгенерированных времен намаза на текущий день."""

    admin_message = ''
