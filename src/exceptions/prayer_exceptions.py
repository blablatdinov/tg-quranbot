from exceptions.base_exception import BaseAppError


class UserPrayersNotFoundError(BaseAppError):
    """У пользователя нет сгенерированных времен намазов."""

    admin_message = ''


class PrayersNotFoundError(BaseAppError):
    """Не найдены времена намазов."""

    admin_message = ''
