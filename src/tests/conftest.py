import random
import uuid

import pytest

from repository.ayats.ayat import Ayat
from repository.users.user import User
from settings import settings
from tests.mocks.ayat_repository import AyatRepositoryMock

pytest_plugins = [
    'tests.plugins.db',
]


@pytest.fixture
def fake_text(faker):
    def _fake_text():  # noqa: WPS430
        return faker.text(10)

    return _fake_text


@pytest.fixture
def user_factory(faker):
    def _user_factory(chat_id: int = None, is_active: bool = True, city_id: int = None):  # noqa: WPS430
        city_id = None if city_id is None else uuid.uuid4()
        return User(
            id=random.randint(1, 9999),
            is_active=is_active,
            day=random.randint(1, 50),
            referrer=None,
            chat_id=chat_id or random.randint(1, 9999),
            city_id=city_id,
        )

    return _user_factory


@pytest.fixture()
def path_to_nominatim_response_fixture():
    return settings.BASE_DIR / 'tests' / 'fixtures' / 'nominatim_response_kazan.json'


@pytest.fixture()
def ayat_factory(fake_text):

    def _ayat_factory(ayat_id: int, ayat_title: str):  # noqa: D102, WPS430
        common_params = {
            'arab_text': fake_text(),
            'content': fake_text(),
            'transliteration': fake_text(),
            'sura_link': fake_text(),
            'audio_telegram_id': fake_text(),
            'link_to_audio_file': fake_text(),
        }
        return Ayat(
            id=ayat_id,
            sura_num=ayat_title.split(':')[0],
            ayat_num=ayat_title.split(':')[1],
            **common_params,
        )

    return _ayat_factory


@pytest.fixture()
def ayat_repository_mock(fake_text):
    mock = AyatRepositoryMock()
    common_params = {
        'arab_text': fake_text(),
        'transliteration': fake_text(),
        'sura_link': fake_text(),
        'audio_telegram_id': fake_text(),
        'link_to_audio_file': fake_text(),
    }
    mock.storage = [
        Ayat(id=1, sura_num=1, ayat_num='1-7', content='content', **common_params),
        Ayat(id=2, sura_num=3, ayat_num='15', content='content', **common_params),
        Ayat(id=3, sura_num=2, ayat_num='10', content='content', **common_params),
        Ayat(id=4, sura_num=2, ayat_num='6,7', content='content', **common_params),
        Ayat(id=5736, sura_num=113, ayat_num='1-6', content='content', **common_params),
        Ayat(id=5737, sura_num=114, ayat_num='1-4', content='content', **common_params),
    ]
    return mock


@pytest.fixture()
def mixer():
    from mixer.backend.sqlalchemy import mixer
    return mixer
