import httpx
from aioredis import Redis

from app_types.stringable import Stringable
from exceptions.content_exceptions import UserHasNotCityIdError
from integrations.tg.chat_id import TgChatId
from integrations.tg.tg_answers import TgAnswerInterface, TgAnswerMarkup, TgAnswerToSender, TgTextAnswer
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
        """Конструктор класса.

        :param prayer_time_answer: TgAnswerInterface
        :param message_answer: TgAnswerInterface
        :param redis: Redis
        """
        self._origin = prayer_time_answer
        self._message_answer = message_answer
        self._redis = redis

    async def build(self, update: Stringable) -> list[httpx.Request]:
        """Сборка ответа.

        :param update: Stringable
        :return: list[httpx.Request]
        """
        try:
            return await self._origin.build(update)
        except UserHasNotCityIdError:
            await LoggedUserState(
                UserState(self._redis, int(TgChatId(update))),
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
