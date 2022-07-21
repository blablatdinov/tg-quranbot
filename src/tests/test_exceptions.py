import pytest

from exceptions.base_exception import BaseAppError
from services.answers.answer_list import AnswersList
from settings import settings


@pytest.fixture
def exception():
    return BaseAppError(message_for_admin_text='oops!!!')


async def test(exception):
    got = await exception.to_answer()

    assert isinstance(got, AnswersList)
    assert got.to_list()[1].chat_id == settings.ADMIN_CHAT_IDS[0]
    assert got.to_list()[1].message == 'oops!!!'
