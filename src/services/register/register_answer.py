from aiogram import types
from loguru import logger

from services.answers.interface import AnswerInterface
from services.register.register_interface import RegisterInterface


class RegisterAnswer(AnswerInterface):
    """Класс осуществляющий регистрацию пользователя."""

    def __init__(
        self,
        register_new_user: RegisterInterface,
        register_user_with_referrer: RegisterInterface,
        register_already_exists_user: RegisterInterface,
        chat_id: int,
    ):
        self._register_new_user = register_new_user
        self._register_user_with_referrer = register_user_with_referrer
        self._register_already_exists_user = register_already_exists_user
        self._chat_id = chat_id

    async def send(self) -> list[types.Message]:
        """Entrypoint.

        :returns: str Ответ пользователю
        """
        logger.info('Process start message for chat_id: {0}'.format(self._chat_id))
        if not await self._register_new_user.can(self._chat_id):
            logger.info('User <{0}> already subscribed'.format(self._chat_id))
            return await self._process_already_subscribed_user()
        if await self._register_user_with_referrer.can(self._chat_id):
            logger.info('Register chat_id: {0} with referrer'.format(self._chat_id))
            return await self._process_with_referrer()
        logger.info('Register new user chat_id: {0} without referrer'.format(self._chat_id))
        return await self._process_without_referrer()

    async def _process_already_subscribed_user(self):
        return await (await self._register_already_exists_user.register(self._chat_id)).send()

    async def _process_with_referrer(self):
        return await (await self._register_user_with_referrer.register(self._chat_id)).send()

    async def _process_without_referrer(self):
        return await (await self._register_new_user.register(self._chat_id)).send()
