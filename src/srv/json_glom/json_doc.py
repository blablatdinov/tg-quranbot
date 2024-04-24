import attrs
from typing import Protocol, final
from pyeo import elegant
from glom import glom


@final
@attrs.define(frozen=True)
@elegant
class Json(Protocol):

    _json_dict: dict

    def path(self, pth: str):
        return glom(self._json_dict, pth)


@final
@attrs.define(frozen=True)
@elegant
class GlomJson(json):

    _json_dict: dict

    def path(self, pth: str):
        return glom(self._json_dict, pth)
