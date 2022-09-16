from integrations.tg.tg_answers.answer_to_sender import TgAnswerToSender
from integrations.tg.tg_answers.interface import TgAnswerInterface
from integrations.tg.tg_answers.message_answer import TgMessageAnswer
from integrations.tg.tg_answers.text_answer import TgTextAnswer


class DebugAnswer(TgAnswerInterface):

    def __init__(self, answer: TgAnswerInterface):
        self._origin = answer

    async def build(self, update):
        return await TgTextAnswer(TgAnswerToSender(TgMessageAnswer(self._origin)), 'debug').build(update)
