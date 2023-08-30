from typing import final, Sequence

import attrs
import httpx
from pyeo import elegant

from app_types.update import Update
from exceptions.prayer_exceptions import PrayersNotFoundError
from integrations.tg.tg_answers import TgAnswer, TgAnswerList, TgAnswerToSender, TgTextAnswer, TgChatIdAnswer, TgMessageAnswer


@final
@attrs.define(frozen=True)
@elegant
class PrayersExpiredAnswer(TgAnswer):

    _origin: TgAnswer
    _empty_answer: TgAnswer
    _admin_chat_ids: Sequence[int]

    async def build(self, update: Update) -> list[httpx.Request]:
        try:
            return await self._origin.build(update)
        except PrayersNotFoundError as err:
            return await TgAnswerList(
                TgTextAnswer(
                    TgAnswerToSender(TgMessageAnswer(self._empty_answer)),
                    'Время намаза на {0} для города {1} не найдено'.format(err.date.strftime('%d.%m.%Y'), err.city_name),
                ),
                TgTextAnswer(
                    TgChatIdAnswer(
                        TgMessageAnswer(self._empty_answer),
                        self._admin_chat_ids[0],
                    ),
                    'Время намаза на {0} для города {1} не найдено'.format(err.date.strftime('%d.%m.%Y'), err.city_name),
                ),
            ).build(update)
