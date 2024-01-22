import glob
import os
import tempfile
from collections import defaultdict
from operator import itemgetter
from pathlib import Path

import pytest
from git import Repo


@pytest.fixture()
def repo_path():
    temp_dir = tempfile.TemporaryDirectory()
    temp_dir_path = Path(temp_dir.name)
    repo = Repo.init(temp_dir_path)
    for filename in 'first', 'second', 'third':
        open(temp_dir_path / filename, 'wb').close()
        repo.index.add([filename])
        repo.index.commit(filename)
    os.mkdir(str(Path(temp_dir_path / 'dir1')))
    Path(temp_dir_path / 'dir1/file_in_dir').write_text('File in directory')
    repo.index.add(['dir1/file_in_dir'])
    repo.index.commit('Create directory')
    Path(temp_dir_path / 'first').write_text('Some changes')
    repo.index.add(['first'])
    repo.index.commit('Some changes')
    os.remove(Path(temp_dir_path / 'second'))
    yield temp_dir_path
    temp_dir.cleanup()


def test(repo_path):
    repo = Repo(repo_path)
    file_change_count = defaultdict(int)
    exists_files = glob.glob('**/*', root_dir=repo_path, recursive=True)
    for commit in repo.iter_commits():
        for item in commit.stats.files.items():
            filename, stats = item
            if filename in exists_files:
                file_change_count[filename] += stats['lines']
    sorted_files = sorted(file_change_count.items(), key=itemgetter(1))
    assert [x[0] for x in sorted_files] == ['third', 'first', 'dir1/file_in_dir']
