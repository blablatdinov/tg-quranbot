from pydantic import BaseModel


class _Address(BaseModel):
    city: str


class NominatimSearchResponse(BaseModel):
    """Модель ответа от сервиса https://nominatim.openstreetmap.org ."""

    display_name: str
    address: _Address
