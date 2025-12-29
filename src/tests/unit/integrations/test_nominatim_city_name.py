# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

import pytest

from integrations.nominatim_city_name import NominatimCityName
from integrations.tg.fk_coordinates import FkCoordinates


@pytest.mark.usefixtures('_mock_nominatim')
async def test():
    got = await NominatimCityName(FkCoordinates(55.7887, 49.1221)).to_str()

    assert got == 'Казань'
