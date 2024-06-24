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

import textwrap
from typing import final

import attrs
from eljson.json import Json
from pyeo import elegant

from srv.ayats.ayat import Ayat, AyatText
from srv.ayats.ayat_identifier import AyatIdentifier
from srv.files.tg_file import TgFile


@final
@attrs.define(frozen=True)
@elegant
class TextLenSafeAyat(Ayat):
    """Декоратор для обрезания текста аята.

    Максимальная длина текстового сообщения: 4096
    https://core.telegram.org/bots/api#sendmessage
    """

    _origin: Ayat

    def identifier(self) -> AyatIdentifier:
        """Идентификатор аята.

        :return: AyatIdentifier
        """
        return self._origin.identifier()

    async def to_str(self) -> AyatText:
        """Строковое представление.

        :return: AyatText
        """
        origin_val = await self._origin.to_str()
        max_len_of_telegram_message = 4096
        if len(origin_val) > max_len_of_telegram_message:
            return textwrap.shorten(origin_val, width=max_len_of_telegram_message, placeholder='...')
        return origin_val

    async def audio(self) -> TgFile:
        """Аудио файл.

        :return: TgFile
        """
        return await self._origin.audio()

    async def change(self, event_body: Json) -> None:
        """Изменить содержимое аята.

        :param event_body: Json
        """
        await self._origin.change(event_body)
