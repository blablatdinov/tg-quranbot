# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final, override

import attrs
from eljson.json import Json

from srv.ayats.ayat import Ayat
from srv.ayats.ayat_identifier import AyatIdentifier
from srv.files.tg_file import TgFile


@final
@attrs.define(frozen=True)
class FkAyat(Ayat):
    """Ayat stub."""

    _id: AyatIdentifier
    _text: str
    _audio: TgFile

    @override
    def identifier(self) -> AyatIdentifier:
        """Идентификатор.

        :return: AyatIdentifier
        """
        return self._id

    @override
    async def to_str(self) -> str:
        """Текст.

        :return: str
        """
        return self._text

    @override
    async def audio(self) -> TgFile:
        """Аудио.

        :return: TgFile
        """
        return self._audio

    @override
    async def change(self, event_body: Json) -> None:
        """Изменить содержимое аята.

        :param event_body: Json
        """
