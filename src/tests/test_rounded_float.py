from app_types.floatable import Floatable
from integrations.tg.tg_answers.measure_answer import RoundedFloat


class FloatableFake(Floatable):

    def __init__(self, origin_float: float):
        self._origin = origin_float

    def __float__(self):
        return self._origin


def test():
    got = float(
        RoundedFloat(
            FloatableFake(0.222), 1
        )
    )

    assert got == 0.2
