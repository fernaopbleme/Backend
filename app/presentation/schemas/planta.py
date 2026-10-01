from typing import Optional

from pydantic import BaseModel


class PlantaResponse(BaseModel):
    id:           int
    nome:         str
    tipo:         str
    data_plantio: str
    foto_url:     Optional[str] = None
