"""The MIT License (MIT).

Copyright (c) 2018-2023 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
OR OTHER DEALINGS IN THE SOFTWARE.
"""
import httpx

from integrations.tg.tg_answers import TgAnswerInterface, TgAnswerList, TgAnswerMarkup, TgTextAnswer
from repository.ayats.schemas import Ayat
from services.answers.answer import FileAnswer, KeyboardInterface, TelegramFileIdAnswer


class AyatAnswer(TgAnswerInterface):
    """Ответ с аятом."""

    def __init__(
        self,
        debug: bool,
        answers: tuple[TgAnswerInterface, TgAnswerInterface],
        ayat: Ayat,
        ayat_answer_keyboard: KeyboardInterface,
    ):
        """Конструктор класса.

        :param debug: bool
        :param answers: tuple[TgAnswerInterface, TgAnswerInterface]
        :param ayat: Ayat
        :param ayat_answer_keyboard: KeyboardInterface
        """
        self._debug_mode = debug
        self._message_answer = answers[0]
        self._file_answer = answers[1]
        self._ayat = ayat
        self._ayat_answer_keyboard = ayat_answer_keyboard

    async def build(self, update) -> list[httpx.Request]:
        """Сборка ответа.

        :param update: Stringable
        :return: list[httpx.Request]
        """
        return await TgAnswerList(
            TgAnswerMarkup(
                TgTextAnswer(
                    self._message_answer,
                    str(self._ayat),
                ),
                self._ayat_answer_keyboard,
            ),
            FileAnswer(
                self._debug_mode,
                TelegramFileIdAnswer(
                    self._file_answer,
                    self._ayat.audio_telegram_id,
                ),
                TgTextAnswer(
                    self._message_answer,
                    self._ayat.link_to_audio_file,
                ),
            ),
        ).build(update)
