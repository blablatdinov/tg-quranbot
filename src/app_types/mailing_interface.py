from aiogram import types


class MailingInterface(object):
    """Интерфейс рассылки."""

    async def send(self) -> list[types.Message]:
        """Отправить.

        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError
