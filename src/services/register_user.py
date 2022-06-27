from dataclasses import dataclass

from repository.admin_message import AdminMessageRepositoryInterface
from repository.ayats import AyatRepositoryInterface
from repository.user import UserRepositoryInterface


@dataclass
class RegisterUser(object):
    """Класс осуществляющий регистрацию пользователя."""

    user_repository: UserRepositoryInterface
    admin_messages_repository: AdminMessageRepositoryInterface
    ayat_service: AyatRepositoryInterface
    chat_id: int

    async def register(self) -> tuple[str, ...]:
        """Entrypoint.

        :returns: str Ответ пользователю
        """
        user_exists = await self.user_repository.exists(self.chat_id)
        if user_exists:
            user = await self.user_repository.get(self.chat_id)
            if user.is_active:
                return 'Вы уже зарегистрированы'

            return 'Рады видеть вас снова, вы продолжите с дня {user_day}'.format(user_day=user.day)

        await self.user_repository.create(self.chat_id)
        start_message = await self.admin_messages_repository.get('start')
        formatted_first_ayat = await self.ayat_service.get_formatted_first_ayat()
        return (start_message, formatted_first_ayat)
