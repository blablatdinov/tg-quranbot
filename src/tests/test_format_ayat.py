from repository.ayats import Ayat, AyatRepositoryInterface
from services.ayat import AyatsService


class AyatRepositoryMock(AyatRepositoryInterface):

    async def first(self) -> Ayat:
        return Ayat(
            sura_num=1,
            ayat_num='1-7',
            arab_text='some arab text',
            content='content',
            transliteration='transliteration',
            sura_link='/some-link',
            audio_telegram_id='some_id',
            link_to_audio_file='some-link',
        )


async def test():
    got = await AyatsService(
        AyatRepositoryMock(),
    ).get_formatted_first_ayat()

    assert got == '<a href="https://umma.ru/some-link">1:1-7)</a>\nsome arab text\n\ncontent\n\n<i>transliteration</i>'
