from app_types.sync_runable import SyncRunable


from pyeo import elegant


from typing import final, override


@final
@elegant
class ForkCliApp(SyncRunable):
    """Маршрутизация для CLI приложения."""

    @override
    def __init__(self, *apps: SyncRunable) -> None:
        """Конструктор класса.

        :param apps: SyncRunable
        """
        self._apps = apps

    @override
    def run(self, args: list[str]) -> int:
        """Запуск.

        :param args: list[str]
        :return: int
        """
        for app in self._apps:
            app.run(args)
        return 0