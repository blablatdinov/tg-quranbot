# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

import textwrap
from typing import final, override

import attrs
from eljson.json import Json

from srv.ayats.ayat import Ayat, AyatText
from srv.ayats.ayat_identifier import AyatIdentifier
from srv.files.tg_file import TgFile


@final
@attrs.define(frozen=True)
class TextLenSafeAyat(Ayat):
    """Декоратор для обрезания текста аята.

    Максимальная длина текстового сообщения: 4096
    https://core.telegram.org/bots/api#sendmessage
    """

    _origin: Ayat

    @override
    def identifier(self) -> AyatIdentifier:
        """Идентификатор аята.

        :return: AyatIdentifier
        """
        return self._origin.identifier()

    @override
    async def to_str(self) -> AyatText:
        """Строковое представление.

        :return: AyatText
        """
        origin_val = await self._origin.to_str()
        max_len_of_telegram_message = 4096
        if len(origin_val) <= max_len_of_telegram_message:
            return origin_val
        buff = max_len_of_telegram_message - origin_val.count('\n')
        res_lines = []
        for line in origin_val.splitlines():
            if buff - len(line) < 0:
                res_lines.append(
                    textwrap.shorten(
                        line,
                        width=buff,
                        placeholder='</i>...' if line.startswith('<i>') else '...',
                    ),
                )
                break
            buff -= len(line)
            res_lines.append(line)
        return '\n'.join(res_lines)

    @override
    async def audio(self) -> TgFile:
        """Аудио файл.

        :return: TgFile
        """
        return await self._origin.audio()

    @override
    async def change(self, event_body: Json) -> None:
        """Изменить содержимое аята.

        :param event_body: Json
        """
        await self._origin.change(event_body)
