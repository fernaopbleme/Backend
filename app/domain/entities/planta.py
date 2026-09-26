from dataclasses import dataclass
from typing import Optional


@dataclass
class Planta:
    nome: str
    tipo: str
    data_plantio: str
    foto_url: Optional[str] = None
    id: Optional[int] = None
