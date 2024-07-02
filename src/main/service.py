# The MIT License (MIT).
#
# Copyright (c) 2013-2024 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
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

import datetime
import tempfile
from operator import itemgetter
from pathlib import Path

from django.conf import settings
from django.template import Context, Template
from git import Repo
from github import Auth, Github

from main.algorithms import files_sorted_by_last_changes, files_sorted_by_last_changes_from_db
from main.models import GhRepo, TouchRecord


def pygithub_client(installation_id: int) -> Github:
    """Pygithub client."""
    auth = Auth.AppAuth(
        874924,
        Path(settings.BASE_DIR / 'revive-code-bot.2024-04-11.private-key.pem').read_text(encoding='utf-8'),
    )
    return Github(auth=auth.get_installation_auth(installation_id))


def process_repo(repo_id: int):
    """Processing repo."""
    gh_repo = GhRepo.objects.get(id=repo_id)
    gh = pygithub_client(gh_repo.installation_id)
    repo = gh.get_repo(gh_repo.full_name)
    gh.close()
    with tempfile.TemporaryDirectory() as tmpdirname:
        Repo.clone_from(repo.clone_url, tmpdirname)
        repo_path = Path(tmpdirname)
        files_for_search = list(repo_path.glob('**/*.py'))
        got = files_sorted_by_last_changes_from_db(
            repo_id,
            files_sorted_by_last_changes(repo_path, files_for_search),
            tmpdirname,
        )
    limit = 10
    stripped_file_list = sorted(
        [
            (
                str(path).replace(
                    '{0}/'.format(tmpdirname),
                    '',
                ),
                points,
            )
            for path, points in got.items()
        ],
        key=itemgetter(1),
        reverse=True,
    )[:limit]
    repo.create_issue(
        'Issue from revive-code-bot',
        Template('\n'.join([
            '{% for file in files %}- [ ] `{{ file }}`\n{% endfor %}\n',
            'Expected actions:\n'
            '1. Create new issues with reference to this issue',
            '2. Clean files must be marked in checklist',
            '3. Close issue',
        ])).render(Context({
            'files': [
                file
                for file, _ in stripped_file_list
            ],
        })),
    )
    TouchRecord.objects.bulk_create([
        TouchRecord(
            gh_repo_id=repo_id,
            path=file,
            date=datetime.datetime.now(tz=datetime.UTC).date(),
        )
        for file, _ in stripped_file_list
        if file not in TouchRecord.objects.values_list('path', flat=True)
    ])
