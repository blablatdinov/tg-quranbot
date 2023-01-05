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
from contextlib import suppress

import httpx

from app_types.stringable import Stringable
from exceptions.user import StartMessageNotContainReferrer, UserAlreadyExists
from integrations.tg.chat_id import TgChatId
from integrations.tg.message_text import MessageText
from integrations.tg.tg_answers import TgAnswerInterface, TgAnswerList, TgAnswerToSender, TgChatIdAnswer, TgTextAnswer
from repository.admin_message import AdminMessageInterface
from repository.ayats.ayat import AyatRepositoryInterface
from repository.users.user import UserRepositoryInterface
from services.start.start_message import StartMessage
from settings import settings


class StartAnswer(TgAnswerInterface):
    """Обработчик стартового сообщения."""

    def __init__(
        self,
        answer: TgAnswerInterface,
        user_repo: UserRepositoryInterface,
        admin_message: AdminMessageInterface,
        ayat_repo: AyatRepositoryInterface,
    ):
        """Конструктор класса.

        :param answer: TgAnswerInterface
        :param user_repo: UserRepositoryInterface
        :param admin_message: AdminMessageInterface
        :param ayat_repo: AyatRepositoryInterface
        """
        self._origin = answer
        self._user_repo = user_repo
        self._admin_message = admin_message
        self._ayat_repo = ayat_repo

    async def build(self, update: Stringable) -> list[httpx.Request]:
        """Собрать ответ.

        :param update: Stringable
        :return: list[httpx.Request]
        """
        await self._check_user_exists(update)
        await self._user_repo.create(int(TgChatId(update)))
        start_message, ayat_message = await self._start_answers()
        create_with_referrer_answers = await self._create_with_referrer(update, start_message, ayat_message)
        if create_with_referrer_answers:
            return create_with_referrer_answers
        return await TgAnswerList(
            TgAnswerToSender(
                TgTextAnswer(
                    self._origin,
                    start_message,
                ),
            ),
            TgAnswerToSender(
                TgTextAnswer(
                    self._origin,
                    ayat_message,
                ),
            ),
            TgChatIdAnswer(
                TgTextAnswer(
                    self._origin,
                    'Зарегистрировался новый пользователь',
                ),
                settings.ADMIN_CHAT_IDS[0],
            ),
        ).build(update)

    async def _start_answers(self) -> tuple[str, str]:
        return (
            await self._admin_message.text(),
            str(await self._ayat_repo.first()),
        )

    async def _check_user_exists(self, update: Stringable) -> None:
        if await self._user_repo.exists(int(TgChatId(update))):
            raise UserAlreadyExists

    async def _create_with_referrer(self, update, start_message, ayat_message) -> list[httpx.Request]:
        with suppress(StartMessageNotContainReferrer):
            referrer_id = await StartMessage(str(MessageText(update)), self._user_repo).referrer_chat_id()
            await self._user_repo.update_referrer(int(TgChatId(update)), referrer_id)
            return await TgAnswerList(
                TgAnswerToSender(
                    TgTextAnswer(
                        self._origin,
                        start_message,
                    ),
                ),
                TgAnswerToSender(
                    TgTextAnswer(
                        self._origin,
                        ayat_message,
                    ),
                ),
                TgChatIdAnswer(
                    TgTextAnswer(
                        self._origin,
                        'По вашей реферальной ссылке произошла регистрация',
                    ),
                    referrer_id,
                ),
                TgChatIdAnswer(
                    TgTextAnswer(
                        self._origin,
                        'Зарегистрировался новый пользователь',
                    ),
                    settings.ADMIN_CHAT_IDS[0],
                ),
            ).build(update)
        return []
