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

"""Test algorithms for define files."""

import datetime
import tempfile
from collections.abc import Generator
from itertools import cycle
from pathlib import Path
from types import ModuleType

import pytest
from django.conf import settings
from faker import Faker
from git import Repo
from time_machine import TimeMachineFixture

from main.algorithms import (
    apply_coefficient,
    code_coverage_rating,
    file_editors_count,
    files_changes_count,
    files_sorted_by_last_changes,
    files_sorted_by_last_changes_from_db,
    lines_count,
    merge_rating,
)
from main.models import GhRepo, TouchRecord

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def gh_repo(baker: ModuleType) -> GhRepo:
    return baker.make('main.GhRepo')  # type: ignore [no-any-return]


@pytest.fixture
def touch_records(baker: ModuleType, gh_repo: GhRepo) -> TouchRecord:
    return baker.make(  # type: ignore [no-any-return]
        'main.TouchRecord',
        path='src/main.py',
        gh_repo=gh_repo,
        date=datetime.date(2024, 7, 1),
    )


@pytest.fixture
def repo_path(faker: Faker, time_machine: TimeMachineFixture) -> Generator[Path, None, None]:
    """Path to temorary git repo."""
    temp_dir = tempfile.TemporaryDirectory()
    temp_dir_path = Path(temp_dir.name)
    repo = Repo.init(temp_dir_path)
    today = datetime.datetime(2024, 4, 20, tzinfo=datetime.UTC)
    time_machine.move_to(today)
    repo.config_writer().set_value('user', 'name', 'First Contributer').release()
    repo.config_writer().set_value('user', 'email', 'first-contributer@github.com').release()
    for filename in 'first.py', 'second.py', 'third.py', 'config.yaml':
        Path(temp_dir_path / filename).write_text('', encoding='utf-8')
        repo.index.add([filename])
        repo.index.commit(filename)
    for i, (name, email) in zip(
        range(6),
        cycle([
            ('First Contributer', 'first-contributer@github.com'),
            ('Second Contributer', 'second-contributer@github.com')],
        ),
    ):
        repo.config_writer().set_value('user', 'name', name).release()
        repo.config_writer().set_value('user', 'email', email).release()
        time_machine.move_to(today + datetime.timedelta(i))
        Path(temp_dir_path / 'first.py').write_text(faker.text(), encoding='utf-8')
        repo.index.add(['first.py'])
        repo.index.commit('Important changes')
    for i in range(5, 7):
        repo.config_writer().set_value('user', 'name', 'Thrird Contributer').release()
        repo.config_writer().set_value('user', 'email', 'thrird-contributer@github.com').release()
        time_machine.move_to(today + datetime.timedelta(i))
        Path(temp_dir_path / 'config.yaml').write_text(faker.text(), encoding='utf-8')
        repo.index.add(['config.yaml'])
        repo.index.commit('Config changes')
    time_machine.move_to(today + datetime.timedelta(15))
    repo.config_writer().set_value('user', 'name', 'First Contributer').release()
    repo.config_writer().set_value('user', 'email', 'first-contributer@github.com').release()
    (Path(temp_dir_path / 'dir1')).mkdir()
    Path(temp_dir_path / 'dir1/file_in_dir.py').write_text('File in directory', encoding='utf-8')
    repo.index.add(['dir1/file_in_dir.py'])
    repo.index.commit('Create directory')
    time_machine.move_to(today + datetime.timedelta(17))
    Path(temp_dir_path / 'first.py').write_text(faker.text(1000), encoding='utf-8')
    repo.index.add(['first.py'])
    repo.index.commit('Some changes')
    (Path(temp_dir_path / 'second.py')).unlink()
    yield temp_dir_path
    temp_dir.cleanup()


def test_files_change_count(repo_path: Path) -> None:
    got = {
        Path(str(file).replace(str(repo_path), '')[1:]): rating
        for file, rating in files_changes_count(repo_path, list(repo_path.glob('**/*.py'))).items()
    }

    assert got == {
        Path('dir1/file_in_dir.py'): 1,
        Path('first.py'): 28,
        Path('third.py'): 0,
    }


def test_last_changes(repo_path: Path, time_machine: TimeMachineFixture) -> None:
    time_machine.move_to('2024-06-02')
    got = {
        Path(str(file).replace(str(repo_path), '')[1:]): rating
        for file, rating in files_sorted_by_last_changes(repo_path, list(repo_path.glob('**/*.py'))).items()
    }

    assert got == {
        Path('dir1/file_in_dir.py'): 28,
        Path('first.py'): 26,
        Path('third.py'): 43,
    }


def test_file_editors_count(repo_path: Path) -> None:
    got = {
        Path(str(file).replace(str(repo_path), '')[1:]): rating
        for file, rating in file_editors_count(repo_path, list(repo_path.glob('**/*.py'))).items()
    }

    assert got == {
        Path('dir1/file_in_dir.py'): 1,
        Path('first.py'): 2,
        Path('third.py'): 1,
    }


def test_merge_real_ratings(repo_path: Path) -> None:
    got = {
        Path(str(file).replace(str(repo_path), '')[1:]): rating
        for file, rating in merge_rating(
            files_sorted_by_last_changes(repo_path, list(repo_path.glob('**/*.py'))),
            files_changes_count(repo_path, list(repo_path.glob('**/*.py'))),
        ).items()
    }

    assert got == {
        Path('dir1/file_in_dir.py'): 3,
        Path('first.py'): 28,
        Path('third.py'): 17,
    }


def test_lines_count(repo_path: Path) -> None:
    got = {
        Path(str(file).replace(str(repo_path), '')[1:]): rating
        for file, rating in lines_count(list(repo_path.glob('**/*.py'))).items()
    }

    assert got == {
        Path('dir1/file_in_dir.py'): 0,
        Path('first.py'): 9,
        Path('third.py'): 0,
    }


@pytest.mark.usefixtures('repo_path')
def test_code_coverage() -> None:
    got = code_coverage_rating((settings.BASE_DIR / 'tests/fixtures/coverage.xml').read_text(encoding='utf-8'))

    assert got == {
        Path('bar.py'): 66,
        Path('foo.py'): 50,
        Path('test.py'): 100,
    }


def test_merge_rating() -> None:
    got = merge_rating(
        {Path('first.py'): 4},
        {Path('first.py'): 6},
        {Path('first.py'): 7, Path('second.py'): 2},
    )

    assert got == {Path('first.py'): 17, Path('second.py'): 2}


def test_apply_coefficient() -> None:
    got = apply_coefficient(
        {Path('first.py'): 5},
        0.5,
    )

    assert got == {Path('first.py'): 2}


@pytest.mark.usefixtures('touch_records')
def test_files_sorted_by_last_changes_from_db(gh_repo: GhRepo, time_machine: TimeMachineFixture) -> None:
    time_machine.move_to('2024-07-01')
    got = files_sorted_by_last_changes_from_db(
        gh_repo.id,
        {
            Path('src/main.py'): 90,
            Path('src/lib.py'): 73,
        },
        Path(),
    )

    assert got == {
        Path('src/main.py'): 0,
        Path('src/lib.py'): 73,
    }
