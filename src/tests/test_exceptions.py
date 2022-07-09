from exceptions import BaseAppError, exception_to_answer_formatter


class CustomException(BaseAppError):
    message = 'custom error message'


async def some_func(foo, bar):
    raise CustomException


async def test():
    got = await exception_to_answer_formatter(some_func)('foo', 'bar')

    assert got.message == 'custom error message'
