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
from typing import final, override

import attrs
from github import Github

from main.models import GhRepo, RepoConfig
from main.services.revive_config.default_revive_config import DefaultReviveConfig
from main.services.revive_config.gh_revive_config import GhReviveConfig
from main.services.revive_config.merged_config import MergedConfig


@final
@attrs.define(frozen=True)
class GhRepoInstallation:
    """Github repository installation."""

    _repos: list
    _installation_id: int
    _gh: Github

    @override
    def register(self):
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
                    'url': 'https://www.rehttp.net/p/https%3A%2F%2Frevive-code-bot.ilaletdinov.ru%2Fhook%2Fgithub',
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
