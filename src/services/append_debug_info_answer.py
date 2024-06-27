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

import httpx
from pyeo import elegant

from app_types.update import Update
from integrations.tg.tg_answers import TgAnswer
from services.DebugParam import DebugParam


@final
@elegant
class AppendDebugInfoAnswer(TgAnswer):
    """Ответ с отладочной информацией."""

    def __init__(self, answer: TgAnswer, *debug_params: DebugParam, debug_mode: bool) -> None:
        """Конструктор класса.

        :param debug_mode: bool
        :param answer: TgAnswerInterface
        :param debug_params: DebugParamInterface
        """
        self._debug = debug_mode
        self._origin = answer
        self._debug_params = debug_params

    @override
    async def build(self, update: Update) -> list[httpx.Request]:
        """Сборка ответа.

        :param update: Update
        :return: list[httpx.Request]
        """
        origin_requests = await self._origin.build(update)
        if not self._debug:
            return origin_requests
        return self._build_new_requests(
            origin_requests,
            [
                await debug_param.debug_value(update)
                for debug_param in self._debug_params
            ],
        )

    def _build_new_requests(self, origin_requests: list[httpx.Request], debug_params: list[str]) -> list[httpx.Request]:
        # TODO #802 Удалить или задокументировать необходимость приватного метода "_build_new_requests"
        debug_str = '\n\n!----- DEBUG INFO -----!\n\n{0}\n\n!----- END DEBUG INFO -----!'.format(
            '\n'.join(debug_params),
        )
        new_requests = []
        for request in origin_requests:
            if 'sendMessage' in str(request.url):
                text = request.url.params['text']
                new_requests.append(httpx.Request(
                    method=request.method,
                    url=request.url.copy_set_param(
                        'text',
                        '{0}{1}'.format(text, debug_str),
                    ),
                    headers=request.headers,
                ))
            else:
                new_requests.append(request)
        return new_requests
