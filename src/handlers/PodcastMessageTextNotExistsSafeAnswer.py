from typing import final

import attrs
import httpx
from pyeo import elegant

from app_types.update import Update
from integrations.tg.tg_answers.tg_answer import TgAnswer
from services.MatchManyJsonPath import MatchManyJsonPath


@final
@attrs.define(frozen=True)
@elegant
class PodcastMessageTextNotExistsSafeAnswer(TgAnswer):
    """В случаи нажатия на кнопку с отсутствующем текстом сообщения."""

    _edited_markup_answer: TgAnswer
    _new_podcast_message_answer: TgAnswer

    async def build(self, update: Update) -> list[httpx.Request]:
        """Трансформация в ответ.

        :param update: Update
        :return: list[httpx.Request]
        """
        try:
            return await self._message_text_exists_case(update)
        except ValueError:
            return await self._new_podcast_message_answer.build(update)

    async def _message_text_exists_case(self, update: Update) -> list[httpx.Request]:
        # TODO #802 Удалить или задокументировать необходимость приватного метода "_message_text_exists_case"
        MatchManyJsonPath(
            update.asdict(),
            ('$..message.text', '$..message.audio'),
        ).evaluate()
        return await self._edited_markup_answer.build(update)
