import pytest
from app_types.update import FkUpdate
from exceptions.internal_exceptions import NotProcessableUpdateError
from integrations.tg.tg_answers import TgAnswerFork, FkAnswer


async def test():
    got = await TgAnswerFork(
        FkAnswer(),
    ).build(FkUpdate)

    assert got[0].url == 'https://some.domain'
    assert len(got) == 1


async def test_not_processable():
    with pytest.raises(NotProcessableUpdateError):
        await TgAnswerFork().build(FkUpdate)
