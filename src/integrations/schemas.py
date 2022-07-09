from pydantic import BaseModel


class NominatimSearchResponse(BaseModel):

    display_name: str
