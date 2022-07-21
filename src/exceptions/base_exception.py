from app_types.answerable import Answerable
from services.answers.answer import Answer
from services.answers.answer_list import AnswersList
from services.answers.interface import AnswerInterface
from settings import settings


class BaseAppError(Exception, Answerable):
    """Базовое исключение бота."""

    user_message: str = 'Произошла какая-то ошибка'
    admin_message: str

    def __init__(self, answer_message: str = None, message_for_admin_text: str = None):
        if answer_message:
            self.user_message = answer_message  # noqa: WPS601
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
