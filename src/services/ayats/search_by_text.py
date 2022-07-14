from typing import Optional

from aiogram.dispatcher import FSMContext

from exceptions import AyatNotFoundError
from repository.ayats.ayat import Ayat, AyatRepositoryInterface
from services.ayats.ayat_search import AyatSearchInterface
from services.ayats.enums import AyatPaginatorCallbackDataTemplate


class AyatSearchByText(AyatSearchInterface):
    """Поиск аята по тексту."""

    ayat_repository: AyatRepositoryInterface
    query: str
    ayat_paginator_callback_data_template = AyatPaginatorCallbackDataTemplate.ayat_text_search_template
    state: FSMContext
    ayat_id: Optional[int] = None

    async def search(self) -> Ayat:
        """Метод, осуществляющий поиск.

        :raises AyatNotFoundError: if ayat not found
        :returns: Ayat
        """
        ayats = await self.ayat_service.search_by_text(self.query)
        if not ayats:
            raise AyatNotFoundError
        await self.state.update_data(search_query=self.query)
        return ayats[0]
