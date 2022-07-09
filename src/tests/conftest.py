import random

import pytest

from repository.user import User
from settings import settings


@pytest.fixture
def fake_text(faker):
    def _fake_text():  # noqa: WPS430
        return faker.text(10)

    return _fake_text


@pytest.fixture
def user_factory(faker):
    def _user_factory(chat_id: int = None, is_active: bool = True, city_id: int = None):  # noqa: WPS430
        city_id = None if city_id == 0 else random.randint(1, 99)
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
    return settings.BASE_DIR / 'tests' / 'fixtures' / 'nominatim_response.json'
