class Runable(object):

    async def run(self):
        raise NotImplementedError


class SyncRunable(object):

    def run(self, args: list[str]) -> int:
        raise NotImplementedError
