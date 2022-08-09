class MailingInterface(object):
    """Интерфейс рассылки."""

    async def send(self):
        """Отправить.

        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError
