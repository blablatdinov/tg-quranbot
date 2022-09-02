import pytest

from repository.users.user import User, UserRepositoryInterface
from services.start_message import StartMessage


class UserRepoMock(UserRepositoryInterface):

    async def get_by_id(self, user_id: int) -> User:
        return User(
            is_active=False,
            day=57,
            chat_id=93475,
            legacy_id=13,
        )


@pytest.mark.parametrize('input_,expected', [
    ('/start 89238', 89238),
    ('/start 13', 93475),
    ('/start 834ruiou', None),
    ('/start {"referrer": 28934}', 28934),
    ('/start', None),
    ('/start {"some_param": "value"}', None),
    ('/start {"referrer":28934}', 28934),
    ('/start {"referrer":"28934iwe"}', None),
])
async def test(input_, expected):
    got = await StartMessage(input_, UserRepoMock()).referrer_id()

    assert got == expected
