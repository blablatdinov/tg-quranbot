from srv.json_glom.json_doc import GlomJson
from app_types.dictable import FkDict


def test():
    got = GlomJson(FkDict({'a': {'b': {'c': 'value'}}})).path('a.b.c')

    assert got == 'value'


def test_json_ctor():
    got = GlomJson.json_ctor('{"a":{"b":{"c":"value"}}}').path('a.b.c')

    assert got == 'value'
