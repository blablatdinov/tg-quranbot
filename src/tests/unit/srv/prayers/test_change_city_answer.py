# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from app_types.fk_update import FkUpdate
from integrations.tg.tg_answers.fk_answer import FkAnswer
from srv.prayers.change_city_answer import ChangeCityAnswer
from srv.prayers.fk_city import FkCity
from srv.prayers.fk_updated_user_city import FkUpdateUserCity


async def test():
    got = await ChangeCityAnswer(
        FkAnswer(),
        FkUpdateUserCity(),
        FkCity.name_ctor('Казань'),
    ).build(FkUpdate.empty_ctor())

    assert got[0].url.params['text'] == 'Вам будет приходить время намаза для города Казань'
