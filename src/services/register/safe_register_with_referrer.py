from databases import Database
from loguru import logger

from services.answers.interface import AnswerInterface
from services.register.register_interface import RegisterInterface


class SafeRegistrationWithReferrer(RegisterInterface):
    """Безопасная регистрация с рефералом.

    В случае если в процессе регистрации с рефералом возникает исключение,
    то вызывается метод для регистрации без реферала
    """

    def __init__(
        self,
        register_with_referrer: RegisterInterface,
        register_new_user: RegisterInterface,
        connection: Database,
    ):
        self._origin = register_with_referrer
        self._register_new_user = register_new_user
        self._connection = connection

    async def register(self, chat_id: int) -> AnswerInterface:
        """Регистрация.

        :param chat_id: int
        :returns: AnswerInterface
        """
        txn = await self._connection.transaction()
        try:
            return await self._origin.register(chat_id)
        except Exception as error:
            logger.error('Error registration with referrer: {0}. Registration without referrer...'.format(str(error)))
            await txn.rollback()
        return await self._register_new_user.register(chat_id)

    async def can(self, chat_id: int) -> bool:
        """Проверка возможности регистрации.

        :param chat_id: int
        :return: bool
        """
        return await self._origin.can(chat_id)
