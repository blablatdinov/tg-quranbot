# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

import pytest

from exceptions.internal_exceptions import UserNotFoundError
from srv.users.chat_id_by_legacy_id import ChatIdByLegacyId


async def test_not_found(pgsql):
    with pytest.raises(UserNotFoundError):
        await ChatIdByLegacyId.int_ctor(pgsql, 1).to_int()
