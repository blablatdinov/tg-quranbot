import datetime
from pathlib import Path

import httpx
from git import Repo

from integrations.tg.tg_answers import TgAnswerInterface
from integrations.tg.tg_answers.update import Update


class DebugParamInterface(object):

    async def value(self, update) -> str:
        raise NotImplementedError


class AppendDebugInfoAnswer(TgAnswerInterface):

    def __init__(self, debug_mode: bool, answer: TgAnswerInterface, *debug_params: DebugParamInterface):
        self._debug = debug_mode
        self._origin = answer
        self._debug_params = debug_params

    async def build(self, update: Update) -> list[httpx.Request]:
        debug_str_list = []
        for param in self._debug_params:
            debug_str_list.append(await param.value(update))
        origin_requests = await self._origin.build(update)
        if not self._debug:
            return origin_requests
        debug_str = '\n\n!----- DEBUG INFO -----!\n\n{0}\n\n!----- END DEBUG INFO -----!'.format('\n'.join(debug_str_list))
        new_requests = []
        for request in origin_requests:
            if 'sendMessage' in str(request.url):
                text = request.url.params['text']
                new_requests.append(httpx.Request(
                    method=request.method,
                    url=request.url.copy_set_param(
                        'text',
                        '{0}{1}'.format(text, debug_str)
                    ),
                    headers=request.headers,
                ))
        return new_requests


class UpdateIdDebugParam(DebugParamInterface):

    async def value(self, update: Update) -> str:
        return 'Update id: {0}'.format(update.update_id)


class TimeDebugParam(DebugParamInterface):

    async def value(self, update: Update) -> str:
        return 'Time: {0}'.format(datetime.datetime.now())


class ChatIdDebugParam(DebugParamInterface):

    async def value(self, update: Update) -> str:
        return 'Chat id: {0}'.format(update.chat_id())


class CommitHashDebugParam(DebugParamInterface):

    def __init__(self, path_to_repo: Path):
        self._path_to_repo = path_to_repo

    async def value(self, update: Update) -> str:
        git_repo = Repo(self._path_to_repo)
        return 'Commit hash: {0}'.format(git_repo.head.commit.hexsha[:6])
