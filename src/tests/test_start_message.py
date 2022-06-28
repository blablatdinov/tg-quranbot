from services.start_message import get_start_message_query


def test_old_format():
    got = get_start_message_query('/start 89238')

    assert got == 89238


def test_new_format():
    got = get_start_message_query('/start {"referrer": 28934}')

    assert got == {'referrer': 28934}


def test_empty_queryes():
    got = get_start_message_query('/start')

    assert got is None