from exceptions.base_exception import BaseAppError


class SuraNotFoundError(BaseAppError):
    """Исключение, вызываемое при отсутсвии нужной суры."""

    user_message = 'Сура не найдена'


class AyatNotFoundError(BaseAppError):
    """Исключение, вызываемое при отсутсвии нужного аята."""

    user_message = 'Аят не найден'


class CityNotSupportedError(BaseAppError):
    """Исключение, вызываемое если при поиске города, он не нашелся в БД."""

    user_message = 'Такой город не обслуживается'


class UserHasNotCityIdError(BaseAppError):
    """Исключение, вызываемое если пользователь без установленного города запросил времена намазов."""

    user_message = 'Вы не указали город, отправьте местоположение или воспользуйтесь поиском'


class AyatHaveNotNeighborsError(BaseAppError):
    """Исключение, вызываемое при попытке сгенерить клавиатуру для аята без соседей."""

    admin_message = 'У аята нет соседей'


class UserHasNotFavoriteAyatsError(BaseAppError):
    """Исключение, вызываемое при попытке получить избранные ааяты, пользователем, у которого их нет."""

    user_message = 'Вы еще не добавляли аятов в избранное'
