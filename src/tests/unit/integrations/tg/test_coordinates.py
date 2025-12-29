# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

import pytest

from app_types.fk_string import FkString
from integrations.tg.tg_message_coordinates import TgMessageCoordinates
from integrations.tg.update import TgUpdate
from settings import BASE_DIR


@pytest.fixture
def coordinates_json():
    return FkString(
        (BASE_DIR / 'tests' / 'fixtures' / 'coordinates.json').read_text(),
    )


def test(coordinates_json):
    coordinates = TgMessageCoordinates(TgUpdate.str_ctor(coordinates_json))

    assert coordinates.latitude() == 40.329649
    assert coordinates.longitude() == -93.599524
