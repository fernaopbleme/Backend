from abc import ABC, abstractmethod
from typing import List, Optional

from app.domain.entities.planta import Planta


class PlantaRepository(ABC):
    @abstractmethod
    def listar(self) -> List[Planta]:
        ...

    @abstractmethod
    def buscar_por_id(self, planta_id: int) -> Optional[Planta]:
        ...

    @abstractmethod
    def criar(self, planta: Planta) -> Planta:
        ...

    @abstractmethod
    def remover(self, planta_id: int) -> None:
        ...
