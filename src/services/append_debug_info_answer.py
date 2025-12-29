# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from collections.abc import Iterable
from typing import final, override

import attrs
import httpx

from app_types.update import Update
from integrations.tg.tg_answers import TgAnswer
from services.debug_param import DebugParam


@final
@attrs.define(frozen=True)
class AppendDebugInfoAnswer(TgAnswer):
    """Ответ с отладочной информацией."""

    _origin: TgAnswer
    _debug_params: Iterable[DebugParam]
    _debug: bool

    @classmethod
    def ctor(cls, answer: TgAnswer, *debug_params: DebugParam, debug_mode: bool) -> TgAnswer:
        """Конструктор класса.

        :param debug_mode: bool
        :param answer: TgAnswerInterface
        :param debug_params: DebugParamInterface
        :return: TgAnswer
        """
        return cls(
            answer,
            debug_params,
            debug_mode,
        )

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

    def _build_new_requests(  # noqa: NPM100. Fix it
        self,
        origin_requests: list[httpx.Request],
        debug_params: list[str],
    ) -> list[httpx.Request]:
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
