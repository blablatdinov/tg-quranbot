"""The MIT License (MIT).

Copyright (c) 2013-2024 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
OR OTHER DEALINGS IN THE SOFTWARE.
"""
import tempfile
from collections import defaultdict
from operator import itemgetter
from os import PathLike
from pathlib import Path

import pytest
from git import Repo


@pytest.fixture()
def repo_path():
    """Path to temorary git repo."""
    temp_dir = tempfile.TemporaryDirectory()
    temp_dir_path = Path(temp_dir.name)
    repo = Repo.init(temp_dir_path)
    for filename in 'first', 'second', 'third':
        Path(temp_dir_path / filename).write_text('')
        repo.index.add([filename])
        repo.index.commit(filename)
    (Path(temp_dir_path / 'dir1')).mkdir()
    Path(temp_dir_path / 'dir1/file_in_dir').write_text('File in directory')
    repo.index.add(['dir1/file_in_dir'])
    repo.index.commit('Create directory')
    Path(temp_dir_path / 'first').write_text('Some changes')
    repo.index.add(['first'])
    repo.index.commit('Some changes')
    (Path(temp_dir_path / 'second')).unlink()
    yield temp_dir_path
    temp_dir.cleanup()


def test(repo_path):
    """Test sorting files for checking."""
    repo = Repo(repo_path)
    file_change_count: dict[str | PathLike[str], int] = defaultdict(int)
    exists_files = list(repo_path.glob('**/*'))
    for commit in repo.iter_commits():
        for item in commit.stats.files.items():
            filename, stats = item
            if (repo_path / filename) in exists_files:
                file_change_count[filename] += stats['lines']
    sorted_files = sorted(file_change_count.items(), key=itemgetter(1))
    assert [x[0] for x in sorted_files] == ['third', 'first', 'dir1/file_in_dir']
