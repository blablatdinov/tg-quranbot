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

from typing import final

import attrs
import pytest
from django.conf import settings

from main.services.github_objs.gh_repo_installation import GhRepoInstallation

pytestmark = [pytest.mark.django_db]


@final
@attrs.define(frozen=True)
class FkContent:

    decoded_content: bytes


@final
@attrs.define(frozen=True)
class FkRepo:

    def create_hook(self, name: str, config: dict[str, str], events: list[str]) -> None:
        pass

    def get_contents(self, name: str) -> FkContent:
        return FkContent(b'limit: 5')


@final
@attrs.define(frozen=True)
class FkGh:

    def get_repo(self, full_name: str) -> FkRepo:
        return FkRepo()


@pytest.fixture
def mock_scheduler(mock_http):
    mock_http.put(
        '{0}/api/jobs'.format(settings.SCHEDULER_HOST),
        status_code=200,
    )
    return mock_http


# TODO: create asserts
@pytest.mark.skip
@pytest.mark.usefixtures('mock_scheduler')
def test() -> None:
    GhRepoInstallation(
        [{'full_name': 'owner_name/repo_name'}],
        1,
    ).register()
