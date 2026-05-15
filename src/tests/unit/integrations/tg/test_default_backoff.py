# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from integrations.tg.default_backoff import DefaultBackoff


def test():
    backoff = list(DefaultBackoff())

    assert len(backoff) > 0
