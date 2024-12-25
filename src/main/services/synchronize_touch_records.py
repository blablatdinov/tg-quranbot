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

"""Synchronize touch records."""

import datetime
from typing import Protocol, final, override

import attrs

from main.models import TouchRecord


class SynchronizeTouchRecords(Protocol):
    """Synchronize touch records."""

    def sync(self, files: list[str], repo_id: int) -> None:
        """Sync."""


@final
@attrs.define(frozen=True)
class PgSynchronizeTouchRecords(SynchronizeTouchRecords):
    """Synchronize touch records."""

    @override
    def sync(self, files: list[str], repo_id: int) -> None:
        """Synching touch records."""
        exists_touch_records = TouchRecord.objects.filter(gh_repo_id=repo_id)
        for tr in exists_touch_records:
            if tr.path in files:
                tr.date = datetime.datetime.now(tz=datetime.UTC).date()
                tr.save()
        for file in files:
            if not TouchRecord.objects.filter(gh_repo_id=repo_id, path=file).exists():
                TouchRecord.objects.create(
                    gh_repo_id=repo_id,
                    path=file,
                    date=datetime.datetime.now(tz=datetime.UTC).date(),
                )
