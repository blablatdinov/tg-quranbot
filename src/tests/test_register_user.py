from services.register_user import RegisterUser
from repository.user import UserRepositoryInterface


class UserRepositoryMock(UserRepositoryInterface):

    def create(self, chat_id: int):
        return


def test():
    got = RegisterUser(
        repository=UserRepositoryMock(),
        chat_id=231,
    )()

    assert got == 'user created'
