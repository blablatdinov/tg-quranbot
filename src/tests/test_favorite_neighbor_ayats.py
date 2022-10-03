import pytest

from repository.ayats.favorite_ayats import FavoriteAyatRepositoryInterface
from repository.ayats.neighbor_ayats import FavoriteNeighborAyats
from repository.ayats.schemas import Ayat


class FavoriteAyatRepositoryFake(FavoriteAyatRepositoryInterface):

    async def get_favorites(self, chat_id: int) -> list[Ayat]:
        return [
            Ayat(
                id=1,
                sura_num=1,
                ayat_num='2',
                arab_text='',
                content='',
                transliteration='',
                sura_link='',
                audio_telegram_id='',
                link_to_audio_file='',
            ),
            Ayat(
                id=2,
                sura_num=1,
                ayat_num='2',
                arab_text='',
                content='',  # noqa: WPS110 wrong variable name
                transliteration='',
                sura_link='',
                audio_telegram_id='',
                link_to_audio_file='',
            ),
            Ayat(
                id=3,
                sura_num=1,
                ayat_num='2',
                arab_text='',
                content='',  # noqa: WPS110 wrong variable name
                transliteration='',
                sura_link='',
                audio_telegram_id='',
                link_to_audio_file='',
            ),
        ]


@pytest.mark.parametrize('ayat_id,expected', [
    (1, 'стр. 1/3'),
    (2, 'стр. 2/3'),
    (3, 'стр. 3/3'),
])
async def test_page(ayat_id, expected):
    got = await FavoriteNeighborAyats(
        ayat_id, 1, FavoriteAyatRepositoryFake(),
    ).page()

    assert got == expected
