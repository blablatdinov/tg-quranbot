# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

import datetime
from typing import final, override

import attrs
import pytz

from app_types.date_time import DateTime
from app_types.update import Update
from exceptions.base_exception import InternalBotError
from services.err_redirect_json_path import ErrRedirectJsonPath
from services.json_path_value import JsonPathValue


@final
@attrs.define(frozen=True)
class TgDateTime(DateTime):
    """Время сообщения."""

    _update: Update

    @override
    def datetime(self) -> datetime.datetime:
        """Дата/время.

        :return: datetime.datetime
        """
        return datetime.datetime.fromtimestamp(
            int(
                ErrRedirectJsonPath(
                    JsonPathValue(
                        self._update.asdict(),
                        '$..date',
                    ),
                    InternalBotError(),
                ).evaluate(),
            ),
            tz=pytz.timezone('UTC'),
        )
