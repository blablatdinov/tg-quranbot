from repository.city import City, CityRepositoryInterface


class CityService(object):
    """Класс для работы с городами."""

    _city_repository: CityRepositoryInterface

    def __init__(self, city_repository: CityRepositoryInterface):
        self._city_repository = city_repository

    async def search_by_name(self, query: str) -> list[City]:
        """Конструктор для поиска по имени.

        :param query: str
        :returns: CityService
        """
        return await self._city_repository.search_by_name(query)
