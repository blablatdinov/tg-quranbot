# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final, override

import attrs
import httpx

from app_types.update import Update
from integrations.tg.tg_answers.tg_answer import TgAnswer
from services.match_many_json_path import MatchManyJsonPath


@final
@attrs.define(frozen=True)
class PodcastMessageTextNotExistsSafeAnswer(TgAnswer):
    """В случаи нажатия на кнопку с отсутствующем текстом сообщения."""

    _edited_markup_answer: TgAnswer
    _new_podcast_message_answer: TgAnswer

    @override
    async def build(self, update: Update) -> list[httpx.Request]:
        """Трансформация в ответ.

        :param update: Update
        :return: list[httpx.Request]
        """
        answer = self._edited_markup_answer
        try:
            MatchManyJsonPath(
                update.asdict(),
                ('$..message.text', '$..message.audio'),
            ).evaluate()
        except ValueError:
            answer = self._new_podcast_message_answer
        return await answer.build(update)
