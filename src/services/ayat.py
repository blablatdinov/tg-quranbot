from dataclasses import dataclass

from repository.ayats.ayat import AyatRepositoryInterface


@dataclass
class AyatServiceInterface(object):
    """Интерфейс для действий над аятами."""

    ayat_repository: AyatRepositoryInterface
    chat_id: int


@dataclass
class AyatsService(AyatServiceInterface):
    """Сервис для действий над аятами."""

    ayat_repository: AyatRepositoryInterface
    chat_id: int
