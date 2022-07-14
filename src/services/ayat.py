from dataclasses import dataclass

from repository.ayats.ayat import AyatRepositoryInterface


@dataclass
class AyatServiceInterface(object):
    """Интерфейс для действий над аятами."""

    ayat_repository: AyatRepositoryInterface
    chat_id: int

    async def search_by_text(self, query: str):
        raise NotImplementedError


@dataclass
class AyatsService(AyatServiceInterface):
    """Сервис для действий над аятами."""

    ayat_repository: AyatRepositoryInterface
    chat_id: int

    async def search_by_text(self, query: str):
        return await self.ayat_repository.search_by_text(query)
