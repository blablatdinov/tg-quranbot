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

"""Test service utils."""

import pytest
from django.conf import settings

from main.service import process_repo
from main.services.github_objs.fk_cloned_repo import FkClonedRepo
from main.services.github_objs.fk_new_issue import FkNewIssue

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def gh_repo(baker):
    repo = baker.make('main.GhRepo')
    baker.make('main.RepoConfig', repo=repo)
    return repo


def test_process_repo_without_disk_config(gh_repo):
    new_issue = FkNewIssue.ctor()
    process_repo(
        gh_repo.id,
        FkClonedRepo(settings.BASE_DIR / 'tests/fixtures/repo-without-config.zip'),
        new_issue,
    )
