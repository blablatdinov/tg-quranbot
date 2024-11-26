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

"""Service utils."""

import tempfile
from pathlib import Path
from typing import TypedDict

import requests
from django.conf import settings
from django.template import Context, Template
from github.GithubException import GithubException

from main.algorithms import files_sorted_by_last_changes, files_sorted_by_last_changes_from_db
from main.models import GhRepo, RepoStatusEnum
from main.services.github_objs.cloned_repo import ClonedRepo
from main.services.github_objs.github_client import pygithub_client
from main.services.github_objs.new_issue import NewIssue
from main.services.revive_config.disk_revive_config import DiskReviveConfig
from main.services.revive_config.gh_revive_config import GhReviveConfig
from main.services.revive_config.merged_config import MergedConfig
from main.services.revive_config.pg_revive_config import PgReviveConfig
from main.services.revive_config.pg_updated_revive_config import PgUpdatedReviveConfig
from main.services.revive_config.revive_config import ConfigDict
from main.services.revive_config.safe_disk_revive_config import SafeDiskReviveConfig
from main.services.synchronize_touch_records import PgSynchronizeTouchRecords


def update_config(repo_full_name: str) -> None:
    """Update config."""
    repo = GhRepo.objects.get(full_name=repo_full_name)
    pg_revive_config = PgReviveConfig(repo.id)
    gh_repo = pygithub_client(repo.installation_id).get_repo(repo.full_name)
    try:
        config = PgUpdatedReviveConfig(
            repo.id,
            MergedConfig.ctor(
                pg_revive_config,
                GhReviveConfig(
                    gh_repo,
                    pg_revive_config,
                ),
            ),
        ).parse()
    except GithubException:
        repo.status = RepoStatusEnum.inactive
        repo.save()
        return
    response = requests.put(
        '{0}/api/jobs'.format(settings.SCHEDULER_HOST),
        {
            'repo_id': repo.id,
            'cron_expression': config['cron'],
        },
        timeout=1,
    )
    response.raise_for_status()


class _Repository(TypedDict):

    default_branch: str
    ref: str


class _RequestForCheckBranchDefault(TypedDict):

    ref: str
    repository: _Repository


def is_default_branch(request_json: _RequestForCheckBranchDefault) -> bool:
    """Check repo branch is default."""
    actual = 'refs/heads/{0}'.format(request_json['repository']['default_branch'])
    default_branch = request_json['ref']
    return actual == default_branch


def process_repo(repo_id: int, cloned_repo: ClonedRepo, new_issue: NewIssue) -> None:
    """Processing repo."""
    with tempfile.TemporaryDirectory() as tmpdirname:
        repo_path = cloned_repo.clone_to(Path(tmpdirname))
        pg_config = PgReviveConfig(repo_id)
        config = PgUpdatedReviveConfig(
            repo_id,
            MergedConfig.ctor(
                pg_config,
                SafeDiskReviveConfig(
                    DiskReviveConfig(repo_path),
                    pg_config,
                ),
            ),
        ).parse()
        got = files_sorted_by_last_changes_from_db(
            repo_id,
            files_sorted_by_last_changes(
                repo_path,
                _define_files_for_search(repo_path, config),
            ),
            repo_path,
        )
    stripped_file_list: list[tuple[str, int]] = _sorted_file_list(repo_path, got)[:config['limit']]
    file_list: list[str] = [file for file, _ in stripped_file_list]
    new_issue.create(
        'Issue from revive-code-bot',
        Template('\n'.join([
            '{% for file in files %}- [ ] `{{ file }}`\n{% endfor %}\n',
            'Expected actions:\n'
            '1. Create new issues with reference to this issue',
            '2. Clean files must be marked in checklist',
            '3. Close issue',
        ])).render(Context({
            'files': file_list,
        })),
    )
    PgSynchronizeTouchRecords().sync(
        file_list,
        repo_id,
    )


def _define_files_for_search(repo_path: Path, config: ConfigDict) -> list[Path]:
    return [
        x
        for x in repo_path.glob(config['glob'] or '**/*')
        if '.git' not in str(x)  # TODO .github/workflows dir case
    ]


def _sorted_file_list(repo_path: Path, file_list: dict[Path, int]) -> list[tuple[str, int]]:
    return sorted(
        [
            (
                str(path).replace(
                    '{0}/'.format(repo_path),
                    '',
                ),
                points,
            )
            for path, points in file_list.items()
        ],
        key=lambda x: (x[1], str(x[0])),
        reverse=True,
    )
