import ujson
import attrs
from app_types.dictable import Dictable, JsonDict
from typing import Protocol, final
from pyeo import elegant
from glom import glom


@final
@attrs.define(frozen=True)
@elegant
class Json(Protocol):

    def path(self, pth: str): ...


@final
@attrs.define(frozen=True)
@elegant
class GlomJson(Json):

    _json_dict: Dictable

    @classmethod
    def json_ctor(cls, raw_json: str) -> Json:
        return cls(JsonDict(raw_json))

    def path(self, pth: str):
        return glom(self._json_dict.to_dict(), pth)
