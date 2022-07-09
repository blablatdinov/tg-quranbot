from pydantic import BaseModel


class NominatimSearchResponse(BaseModel):
    """Модель ответа от сервиса https://nominatim.openstreetmap.org ."""

    display_name: str
