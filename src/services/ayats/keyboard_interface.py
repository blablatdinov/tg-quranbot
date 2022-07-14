class AyatSearchKeyboardInterface(object):
    """Интерфейс для клавиатур."""

    async def generate(self):
        """Сгенерировать клавиатуру.

        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError
