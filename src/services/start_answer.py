from contextlib import suppress

import httpx

from exceptions.base_exception import BaseAppError
from exceptions.user import StartMessageNotContainReferrer, UserAlreadyExists
from integrations.tg.tg_answers import TgAnswerInterface, TgAnswerList, TgAnswerToSender, TgChatIdAnswer, TgTextAnswer
from integrations.tg.tg_answers.update import Update
from repository.admin_message import AdminMessageRepositoryInterface
from repository.ayats.ayat import AyatRepositoryInterface
from repository.users.user import UserRepositoryInterface
from repository.users.users import UsersRepositoryInterface
from services.regular_expression import IntableRegularExpression
from settings import settings


class StartMessage(object):
    """Стартовое сообщение."""

    def __init__(self, message: str, user_repo: UserRepositoryInterface):
        self._message = message
        self._user_repo = user_repo

    async def referrer_chat_id(self) -> int:
        """Получить идентификатор пригласившего.

        :return: int
        :raises StartMessageNotContainReferrer: if message not contain referrer id
        """
        try:
            message_meta = int(IntableRegularExpression(self._message))
        except BaseAppError as err:
            raise StartMessageNotContainReferrer from err
        max_legacy_id = 3000
        if message_meta < max_legacy_id:
            return (await self._user_repo.get_by_id(message_meta)).chat_id
        return message_meta


class SafeStartAnswer(TgAnswerInterface):
    """Декоратор обработчика стартового сообщение с предохранением от UserAlreadyExists."""

    def __init__(
        self,
        start_answer: TgAnswerInterface,
        sender_answer: TgAnswerInterface,
        user_repo: UserRepositoryInterface,
        users_repo: UsersRepositoryInterface,
    ):
        self._origin = start_answer
        self._user_repo = user_repo
        self._sender_answer = sender_answer
        self._users_repo = users_repo

    async def build(self, update: Update) -> list[httpx.Request]:
        """Собрать ответ.

        :param update: Update
        :return: list[httpx.Request]
        """
        with suppress(UserAlreadyExists):
            return await self._origin.build(update)
        user = await self._user_repo.get_by_chat_id(update.chat_id())
        if user.is_active:
            return await TgTextAnswer(
                self._sender_answer,
                'Вы уже зарегистрированы!',
            ).build(update)
        await self._users_repo.update_status([update.chat_id()], to=True)
        return await TgTextAnswer(
            self._sender_answer,
            'Рады видеть вас снова, вы продолжите с дня {0}'.format(user.day),
        ).build(update)


class StartAnswer(TgAnswerInterface):
    """Обработчик стартового сообщения."""

    def __init__(
        self,
        answer: TgAnswerInterface,
        user_repo: UserRepositoryInterface,
        admin_message_repo: AdminMessageRepositoryInterface,
        ayat_repo: AyatRepositoryInterface,
    ):
        self._origin = answer
        self._user_repo = user_repo
        self._admin_message_repo = admin_message_repo
        self._ayat_repo = ayat_repo

    async def build(self, update: Update) -> list[httpx.Request]:
        """Собрать ответ.

        :param update: Update
        :return: list[httpx.Request]
        """
        await self._check_user_exists(update)
        await self._user_repo.create(update.chat_id())
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
            await self._admin_message_repo.get('start'),
            str(await self._ayat_repo.first()),
        )

    async def _check_user_exists(self, update) -> None:
        if await self._user_repo.exists(update.chat_id()):
            raise UserAlreadyExists

    async def _create_with_referrer(self, update, start_message, ayat_message) -> list[httpx.Request]:
        with suppress(StartMessageNotContainReferrer):
            referrer_id = await StartMessage(update.message().text(), self._user_repo).referrer_chat_id()
            await self._user_repo.update_referrer(update.chat_id(), referrer_id)
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
