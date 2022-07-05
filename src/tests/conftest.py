import random

import pytest

from repository.user import User


@pytest.fixture
def fake_text(faker):
    def _fake_text():  # noqa: WPS430
        return faker.text(10)

    return _fake_text


@pytest.fixture
def user_factory(faker):
    def _user_factory(chat_id: int = None, is_active: bool = True):  # noqa: WPS430
        return User(
            id=random.randint(1, 9999),
            is_active=is_active,
            day=random.randint(1, 50),
            referrer=None,
            chat_id=chat_id or random.randint(1, 9999),
            city_id=random.randint(1, 99),
        )

    return _user_factory
