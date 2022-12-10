from pathlib import Path

import pytest

from app_types.stringable import ThroughStringable
from integrations.tg.coordinates import TgMessageCoordinates


@pytest.fixture()
def coordinates_json():
    return ThroughStringable(
        (Path(__file__).parent / 'fixtures' / 'coordinates.json').read_text(),
    )


def test(coordinates_json):
    coordinates = TgMessageCoordinates(coordinates_json)

    assert coordinates.latitude() == 40.329649
    assert coordinates.longitude() == -93.599524
