# The MIT License (MIT).
#
# Copyright (c) 2018-2024 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
# OR OTHER DEALINGS IN THE SOFTWARE.

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
