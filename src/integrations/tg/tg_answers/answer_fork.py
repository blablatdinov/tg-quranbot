from contextlib import suppress

import httpx

from app_types.stringable import Stringable
from exceptions.internal_exceptions import (
    CallbackQueryNotFoundError,
    CoordinatesNotFoundError,
    InlineQueryNotFoundError,
    MessageIdNotFoundError,
    NotProcessableUpdateError,
)
from integrations.tg.tg_answers.interface import TgAnswerInterface


class TgAnswerFork(TgAnswerInterface):
    """Маршрутизация ответов."""

    def __init__(self, *answers: TgAnswerInterface):
        self._answers = answers

    async def build(self, update: Stringable) -> list[httpx.Request]:
        """Собрать ответ.

        :param update: Stringable
        :return: list[httpx.Request]
        :raises NotProcessableUpdateError: if not found matches
        """
        for answer in self._answers:
            with suppress(
                CoordinatesNotFoundError, CallbackQueryNotFoundError, MessageIdNotFoundError, InlineQueryNotFoundError,
            ):
                origin_requests = await answer.build(update)
                if origin_requests:
                    return origin_requests
        raise NotProcessableUpdateError
