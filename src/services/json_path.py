# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import Protocol, TypeVar

ET_co = TypeVar('ET_co', covariant=True)


class JsonPath(Protocol[ET_co]):
    """Интерфейс объектов, получающих значение по jsonpath."""

    def evaluate(self) -> ET_co:
        """Получить значение."""
