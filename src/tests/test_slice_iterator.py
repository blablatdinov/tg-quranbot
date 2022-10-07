from integrations.tg.sendable import SliceIterator


def test():
    got = list(SliceIterator(list(range(1, 11)), 2))

    assert got == [
        [1, 2],
        [3, 4],
        [5, 6],
        [7, 8],
        [9, 10],
    ]


def test_other_slice_size():
    got = list(SliceIterator(list(range(1, 10)), 5))

    assert got == [
        [1, 2, 3, 4, 5],
        [6, 7, 8, 9],
    ]
