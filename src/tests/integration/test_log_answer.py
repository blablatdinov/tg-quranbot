import pytest
from aiogram import types

from repository.update_log import UpdatesLogRepository
from services.answers.interface import AnswerInterface
from services.answers.log_answer import LoggedAnswer, LoggedSourceMessageAnswerProcess


@pytest.fixture()
def message():
    def _message(message_id, text):  # noqa: WPS430
        return types.Message(**{  # noqa: WPS517
            'message_id': message_id,
            'from': {
                'id': 12345678,
                'is_bot': False,
                'first_name': 'FirstName',
                'last_name': 'LastName',
                'username': 'username',
                'language_code': 'ru',
            },
            'chat': {
                'id': 12345678,
                'first_name': 'FirstName',
                'last_name': 'LastName',
                'username': 'username',
                'type': 'private',
            },
            'date': 1508709711,
            'text': text,
        })

    return _message


class AnswerMock(AnswerInterface):

    def __init__(self, return_message: types.Message):
        self._return_message = return_message

    async def send(self, chat_id):
        return [self._return_message]

    async def edit_markup(self, message_id: int, chat_id: int = None):
        pass

    def to_list(self):
        pass


async def test_log_answer(db_session, message):
    await LoggedSourceMessageAnswerProcess(
        UpdatesLogRepository(db_session),
        message(321, 'Подкасты'),
        LoggedAnswer(
            AnswerMock(
                message(123, 'Podcast answer text'),
            ),
            UpdatesLogRepository(db_session),
        ),
    ).send()

    rows = await db_session.fetch_all('SELECT message_id, text FROM bot_init_message ORDER BY id DESC LIMIT 2')
    rows_as_dict_list = [dict(row._mapping) for row in rows]  # noqa: WPS437

    assert [row['text'] for row in rows_as_dict_list] == ['Podcast answer text', 'Подкасты']
    assert [row['message_id'] for row in rows_as_dict_list] == [123, 321]
