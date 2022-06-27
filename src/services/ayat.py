from repository.ayats import AyatRepositoryInterface


class AyatServiceInterface(object):
    """Интерфейс для действий над аятами."""

    ayat_repository: AyatRepositoryInterface

    async def get_formatted_first_ayat(self, id_: int) -> str:
        """Получить отформатированный аят.

        :param id_: str
        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError


class AyatsService(AyatServiceInterface):
    """Сервис для действий над аятами."""

    ayat_repository: AyatRepositoryInterface

    async def get_formatted_first_ayat(self, id_: int) -> str:
        """Получить отформатированный аят.

        :param id_: str
        :returns: str
        """
        return await self.ayat_repository.first()
