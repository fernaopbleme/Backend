from typing import List

from app.domain.entities.planta import Planta
from app.domain.repositories.planta_repository import PlantaRepository


class ListarPlantas:
    def __init__(self, repositorio: PlantaRepository):
        self._repositorio = repositorio

    def executar(self) -> List[Planta]:
        return self._repositorio.listar()
