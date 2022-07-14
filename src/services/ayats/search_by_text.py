from repository.ayats.ayat import AyatRepositoryInterface
from services.ayats.ayat_search import AyatSearchInterface


class AyatSearchByText(AyatSearchInterface):

    ayat_repository: AyatRepositoryInterface
    query: str
    ayat_paginator_callback_data_template = AyatPaginatorCallbackDataTemplate.ayat_text_search_template
    state: FSMContext
    ayat_id: Optional[int] = None

    async def search(self) -> Ayat:
        """Метод, осуществляющий поиск.

        """
        ayats = await self.ayat_service.search_by_text(self.query)
        if not ayats:
            raise AyatNotFoundError
        await self.state.update_data(search_query=self.query)
        return ayats[0]
