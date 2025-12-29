# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import Protocol, TypeAlias

from eljson.json import Json

from app_types.async_supports_str import AsyncSupportsStr
from srv.ayats.ayat_identifier import AyatIdentifier
from srv.files.tg_file import TgFile

AyatText: TypeAlias = str


class Ayat(AsyncSupportsStr, Protocol):
    """Интерфейс аята."""

    def identifier(self) -> AyatIdentifier:
        """Идентификатор аята."""

    async def to_str(self) -> AyatText:
        """Строковое представление."""

    async def audio(self) -> TgFile:
        """Аудио файл."""

    async def change(self, event_body: Json) -> None:
        """Изменить содержимое аята.

        :param event_body: Json
        """
