from repository.ayats.schemas import Ayat


class AyatSearchInterface(object):
    """Интерфейс класса, осуществляющего поиск аятов."""

    async def search(self) -> Ayat:
        """Метод, осуществляющий поиск.

        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError
