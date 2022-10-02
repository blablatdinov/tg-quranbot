from exceptions.base_exception import BaseAppError


class UserAlreadyExists(BaseAppError):
    """Пользователь уже зарегистрирован."""

    admin_message = ''


class StartMessageNotContainReferrer(BaseAppError):
    """Стартовое сообщение не содержит информации о пригласившем."""

    admin_message = ''
