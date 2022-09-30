import httpx
from aioredis import Redis

from exceptions.content_exceptions import UserHasNotCityIdError
from integrations.tg.tg_answers import TgAnswerInterface, TgAnswerMarkup, TgAnswerToSender, TgTextAnswer
from integrations.tg.tg_answers.update import Update
from services.switch_inline_query_answer import SwitchInlineQueryKeyboard
from services.user_state import LoggedUserState, UserState, UserStep


class InviteSetCityAnswer(TgAnswerInterface):
    """Ответ с приглашением ввести город."""

    def __init__(
        self,
        prayer_time_answer: TgAnswerInterface,
        message_answer: TgAnswerInterface,
        redis: Redis,
    ):
        self._origin = prayer_time_answer
        self._message_answer = message_answer
        self._redis = redis

    async def build(self, update: Update) -> list[httpx.Request]:
        """Сборка ответа.

        :param update: Update
        :return: list[httpx.Request]
        """
        try:
            return await self._origin.build(update)
        except UserHasNotCityIdError:
            await LoggedUserState(
                UserState(self._redis, update.chat_id()),
            ).change_step(UserStep.city_search)
            return await TgAnswerMarkup(
                TgAnswerToSender(
                    TgTextAnswer(
                        self._message_answer,
                        'Вы не указали город, отправьте местоположение или воспользуйтесь поиском',
                    ),
                ),
                SwitchInlineQueryKeyboard(),
            ).build(update)
