from .settings import AppSettings


class Container:
    def __init__(self, settings: AppSettings) -> None:
        self._settings = settings

    async def aclose(self) -> None:
        pass
