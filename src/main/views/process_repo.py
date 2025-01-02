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

"""HTTP controller for process repo."""

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from main.exceptions import UnavailableRepoError
from main.models import GhRepo, RepoStatusEnum
from main.service import process_repo
from main.services.github_objs.gh_cloned_repo import GhClonedRepo
from main.services.github_objs.gh_new_issue import GhNewIssue
from main.services.github_objs.github_client import github_repo


@csrf_exempt
def process_repo_view(request: HttpRequest, repo_id: int) -> HttpResponse:
    """Webhook for process repo."""
    if request.headers['Authentication'] != 'Basic {0}'.format(settings.BASIC_AUTH_TOKEN):
        raise PermissionDenied
    repo = get_object_or_404(GhRepo, id=repo_id)
    try:
        process_repo(
            repo.id,
            GhClonedRepo(repo),
            GhNewIssue(github_repo(repo.installation_id, repo.full_name)),
        )
    except UnavailableRepoError:
        repo.status = RepoStatusEnum.inactive
        repo.save()
    return HttpResponse(status=201)
