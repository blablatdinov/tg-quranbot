# The MIT License (MIT).
#
# Copyright (c) 2023-2024 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
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

"""Github repository installation."""

import random
from typing import Protocol, final, override

import attrs
import requests
from django.conf import settings
from github import Github

from main.models import GhRepo, RepoConfig
from main.services.github_objs.repo_installation import RegisteredRepoFromGithub
from main.services.revive_config.default_revive_config import DefaultReviveConfig
from main.services.revive_config.gh_revive_config import GhReviveConfig
from main.services.revive_config.merged_config import MergedConfig


class RepoInstallation(Protocol):
    """Repository installation."""

    def register(self) -> None:
        """Registering new repositories."""


@final
@attrs.define(frozen=True)
class GhRepoInstallation(RepoInstallation):
    """Github repository installation."""

    _repos: list[RegisteredRepoFromGithub]
    _installation_id: int
    _gh: Github

    @override
    def register(self) -> None:
        """Registering new repositories."""
        for repo in self._repos:
            repo_db_record = GhRepo.objects.create(
                full_name=repo['full_name'],
                installation_id=self._installation_id,
                has_webhook=False,
            )
            gh_repo = self._gh.get_repo(repo['full_name'])
            # TODO: query may be failed, because already created
            gh_repo.create_hook(
                'web',
                {
                    'url': 'https://www.rehttp.net/p/https://revive-code-bot.ilaletdinov.ru/hook/github',
                    'content_type': 'json',
                },
                ['issues', 'issue_comment', 'push'],
            )
            config = MergedConfig.ctor(
                GhReviveConfig(
                    gh_repo,
                    DefaultReviveConfig(random),
                ),
            )
            RepoConfig.objects.create(
                repo=repo_db_record,
                cron_expression=config.parse()['cron'],
            )
            response = requests.put(
                '{0}/api/jobs'.format(settings.SCHEDULER_HOST),
                {
                    'repo_id': repo_db_record.id,
                    'cron_expression': config.parse()['cron'],
                },
                timeout=1,
            )
            response.raise_for_status()
