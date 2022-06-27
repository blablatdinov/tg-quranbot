import pytest

from repository.ayats import Ayat, AyatRepositoryInterface
from services.ayat import AyatsService

pytestmark = [pytest.mark.asyncio]


class AyatRepositoryMock(AyatRepositoryInterface):

    async def first(self) -> Ayat:
        return Ayat(
            sura_num=1,
            ayat_num='1-7',
            arab_text='some arab text',
            content='content',
            transliteration='transliteration',
        )


async def test():
    got = await AyatsService(
        AyatRepositoryMock(),
    ).get_formatted_first_ayat()

    assert got == '<a href="#">1:1-7)</a>some arab text\n\ncontent\n\n<i>transliteration</i>'
