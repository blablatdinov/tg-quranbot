from db import db_connection
from exceptions import BaseAppError, exception_to_answer_formatter
from integrations.client import IntegrationClient
from integrations.nominatim import NominatimIntegration
from repository.city import CityRepository
from services.city import CitiesCoordinatesSearch, Cities


class CustomException(BaseAppError):
    message = 'custom error message'


async def some_func(foo, bar):
    raise CustomException


async def test():
    got = await exception_to_answer_formatter(some_func)('foo', 'bar')

    assert got.message == 'custom error message'


# FIXME delete
async def test_simple():
    async with db_connection() as connection:
        got = await CitiesCoordinatesSearch(
            Cities([], CityRepository(connection)),
            NominatimIntegration(
                IntegrationClient(),
            ),
            # '55.76728145852831',
            # '49.100915750000006',
            '0',
            '0',
        ).to_answer()

    assert False, got
