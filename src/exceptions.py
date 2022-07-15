from answerable import Answerable
from services.answer import Answer, AnswerInterface, AnswersList
from settings import settings


class BaseAppError(Exception, Answerable):
    """Базовое исключение бота."""

    user_message = 'Произошла какая-то ошибка'
    admin_message: str

    def __init__(self, answer_message: str = None, message_for_admin_text: str = None):
        if answer_message:
            self.user_message = answer_message
        # TODO: get traceback
        self.admin_message = message_for_admin_text or ''

    async def to_answer(self) -> AnswerInterface:
        """Конвертирует объект в AnswerInterface.

        :returns: AnswerInterface
        """
        return AnswersList(
            Answer(message=self.user_message),
            Answer(message=self.admin_message, chat_id=settings.ADMIN_CHAT_IDS[0]),
        )


class InternalBotError(BaseAppError):
    """Внутренняя ошибка бота."""

    user_message = ''


class SuraNotFoundError(BaseAppError):
    """Исключение, вызываемое при отсутсвии нужной суры."""

    user_message = 'Сура не найдена'


class AyatNotFoundError(BaseAppError):
    """Исключение, вызываемое при отсутсвии нужного аята."""

    user_message = 'Аят не найден'


class CityNotSupportedError(BaseAppError):
    """Исключение, вызываемое если при поиске города, он не нашелся в БД."""

    user_message = 'Такой город не обслуживается'


class UserHasNotCityIdError(BaseAppError):
    """Исключение, вызываемое если пользователь без установленного города запросил времена намазов."""

    user_message = 'Вы не указали город, отправьте местоположение или воспользуйтесь поиском'


class AyatHaveNotNeighborsError(BaseAppError):
    """Исключение, вызываемое при попытке сгенерить клавиатуру для аята без соседей."""

    admin_message = 'У аята нет соседей'
