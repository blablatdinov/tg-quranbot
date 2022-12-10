import httpx

from app_types.stringable import Stringable
from integrations.tg.tg_answers.answer_to_sender import TgAnswerToSender
from integrations.tg.tg_answers.interface import TgAnswerInterface
from integrations.tg.tg_answers.message_answer import TgMessageAnswer
from integrations.tg.tg_answers.text_answer import TgTextAnswer
from integrations.tg.update_id import UpdateId


class DebugAnswer(TgAnswerInterface):
    """Ответ для отладки."""

    def __init__(self, answer: TgAnswerInterface):
        self._origin = answer

    async def build(self, update: Stringable) -> list[httpx.Request]:
        """Сборка ответа.

        :param update: Stringable
        :returns: list[httpx.Request]
        """
        return await TgTextAnswer(
            TgAnswerToSender(
                TgMessageAnswer(self._origin),
            ),
            'DEBUG. Update <{0}>'.format(int(UpdateId(update))),
        ).build(update)
