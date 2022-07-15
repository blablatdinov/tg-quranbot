from repository.ayats.ayat import Ayat, AyatRepositoryInterface
from services.ayats.enums import AyatPaginatorCallbackDataTemplate


class AyatSearchInterface(object):
    """Интерфейс класса, осуществляющего поиск аятов."""

    ayat_repository: AyatRepositoryInterface
    ayat_paginator_callback_data_template: AyatPaginatorCallbackDataTemplate

    async def search(self) -> Ayat:
        """Метод, осуществляющий поиск.

        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError
