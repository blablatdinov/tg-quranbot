# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from app_types.fk_float import FkFloat
from app_types.rounded_float import RoundedFloat


def test():
    got = float(
        RoundedFloat(
            FkFloat(0.222), 1,
        ),
    )

    assert got == 0.2
