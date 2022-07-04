import pytest

from repository.ayats.ayat import Ayat
from tests.mocks.ayat_repository import AyatRepositoryMock


@pytest.fixture()
def ayat_repository_mock(fake_text):
    mock = AyatRepositoryMock()
    common_params = {
        'arab_text': fake_text(),
        'content': fake_text(),
        'transliteration': fake_text(),
        'sura_link': fake_text(),
        'audio_telegram_id': fake_text(),
        'link_to_audio_file': fake_text(),
    }
    mock.storage = [
        Ayat(id=1, sura_num=1, ayat_num='1-7', **common_params),
        Ayat(id=2, sura_num=3, ayat_num='15', **common_params),
        Ayat(id=3, sura_num=2, ayat_num='10', **common_params),
        Ayat(id=4, sura_num=2, ayat_num='6,7', **common_params),
        Ayat(id=5737, sura_num=114, ayat_num='1-4', **common_params),
    ]
    return mock
