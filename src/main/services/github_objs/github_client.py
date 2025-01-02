# The MIT License (MIT).
#
# Copyright (c) 2023-2025 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
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

# TODO: rename file

"""Creating github client."""

from collections.abc import Iterable
from contextlib import suppress
from pathlib import Path
from typing import Protocol, final

import attrs
from django.conf import settings
from github import Auth, Github
from github.GithubException import GithubException, UnknownObjectException
from github.Repository import Repository

from main.exceptions import UnavailableRepoError


class RepoFetchMethod(Protocol):
    """Fetch github repo."""

    def fetch(self) -> Repository:
        """Fetch github repo."""


@final
@attrs.define(frozen=True)
class RepoFetchStrategy(RepoFetchMethod):
    """Fetch github repo."""

    _methods: Iterable[RepoFetchMethod]

    @classmethod
    def ctor(cls, *methods: RepoFetchMethod) -> RepoFetchMethod:
        """Ctor."""
        return cls(methods)

    def fetch(self) -> Repository:
        """Fetch github repo."""
        for method in self._methods:
            with suppress(GithubException, UnknownObjectException):
                return method.fetch()
        raise UnavailableRepoError


@final
@attrs.define(frozen=True)
class InstallationFetchRepo(RepoFetchMethod):
    """Fetch github repo."""

    _installation_id: int
    _full_name: str

    def fetch(self) -> Repository:
        """Fetch github repo."""
        return Github(
            auth=Auth.AppAuth(
                874924,
                Path(settings.BASE_DIR / 'revive-code-bot.private-key.pem').read_text(encoding='utf-8'),
            ).get_installation_auth(self._installation_id),
        ).get_repo(self._full_name)


@final
@attrs.define(frozen=True)
class GhUserBotFetchRepo(RepoFetchMethod):
    """Fetch github repo."""

    _full_name: str

    def fetch(self) -> Repository:
        """Fetch github repo."""
        return Github(
            auth=Auth.Token(settings.GH_TOKEN),
        ).get_repo(self._full_name)


def github_repo(installation_id: int, full_name: str) -> Repository:
    """Fetch github repo.

    TODO: make object
    """
    return RepoFetchStrategy.ctor(
        InstallationFetchRepo(installation_id, full_name),
        GhUserBotFetchRepo(full_name),
    ).fetch()
