from typing import Callable

from services.answer import Answer, AnswerInterface


class BaseAppError(Exception):
    """Базовое исключение бота."""

    message = 'Произошла какая-то ошибка'

    def __init__(self, answer_message: str = None):
        if answer_message:
            self.message = answer_message  # noqa: WPS601

    def to_answer(self) -> AnswerInterface:
        """Конвертирует объект в AnswerInterface.

        :returns: AnswerInterface
        """
        return Answer(message=self.message)


class InternalBotError(BaseAppError):
    """Внутренняя ошибка бота."""

    message = ''


class SuraNotFoundError(BaseAppError):
    """Исключение, вызываемое при отсутсвии нужной суры."""

    message = 'Сура не найдена'


class AyatNotFoundError(BaseAppError):
    """Исключение, вызываемое при отсутсвии нужного аята."""

    message = 'Аят не найден'


class CityNotSupportedError(BaseAppError):
    """Исключение, вызываемое если при поиске города, он не нашелся в БД."""

    message = 'Такой город не обслуживается'


class UserHasNotCityIdError(BaseAppError):
    """Исключение, вызываемое если пользователь без установленного города запросил времена намазов."""

    message = 'Вы не указали город, отправьте местоположение или воспользуйтесь поиском'


class AyatHaveNotNeighbors(BaseAppError):

    pass


def exception_to_answer_formatter(func: Callable):
    """Декоратор обрабатывающий ошибки бота и возвращающий из них AnswerInterface.

    :param func: Callable
    :returns: Callable
    """
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except BaseAppError as bot_error:
            return bot_error.to_answer()

    return wrapper
