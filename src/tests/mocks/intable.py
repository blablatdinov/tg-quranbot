from app_types.intable import Intable


class IntableMock(Intable):

    def __init__(self, input_: int):
        self.origin = input_

    def __int__(self):
        return self.origin
