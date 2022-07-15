from pydantic import BaseModel


class CountResult(BaseModel):
    """Результат запроса с кол-вом."""

    count: int
