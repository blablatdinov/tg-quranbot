import pytest


@pytest.fixture
def fake_text(faker):
    def _fake_text():  # noqa: WPS430
        return faker.text(10)

    return _fake_text
