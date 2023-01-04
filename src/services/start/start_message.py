from exceptions.base_exception import BaseAppError
from exceptions.user import StartMessageNotContainReferrer
from repository.users.user import UserRepositoryInterface
from services.regular_expression import IntableRegularExpression


class StartMessage(object):
    """Стартовое сообщение."""

    def __init__(self, message: str, user_repo: UserRepositoryInterface):
        """Конструктор класса.

        :param message: str
        :param user_repo: UserRepositoryInterface
        """
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
