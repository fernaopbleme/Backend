from typing import List, Optional

from sqlalchemy.orm import Session

from app.domain.entities.planta import Planta
from app.domain.repositories.planta_repository import PlantaRepository
from app.infrastructure.persistence.models import PlantaModel


class SqlAlchemyPlantaRepository(PlantaRepository):
    def __init__(self, session: Session):
        self._session = session

    def listar(self) -> List[Planta]:
        return [self._para_entidade(m) for m in self._session.query(PlantaModel).all()]

    def buscar_por_id(self, planta_id: int) -> Optional[Planta]:
        modelo = self._buscar_modelo(planta_id)
        return self._para_entidade(modelo) if modelo is not None else None

    def criar(self, planta: Planta) -> Planta:
        modelo = PlantaModel(
            nome         = planta.nome,
            tipo         = planta.tipo,
            data_plantio = planta.data_plantio,
            foto_url     = planta.foto_url,
        )
        self._session.add(modelo)
        self._session.commit()
        self._session.refresh(modelo)
        return self._para_entidade(modelo)

    def remover(self, planta_id: int) -> None:
        modelo = self._buscar_modelo(planta_id)
        if modelo is not None:
            self._session.delete(modelo)
            self._session.commit()

    def _buscar_modelo(self, planta_id: int) -> Optional[PlantaModel]:
        return self._session.query(PlantaModel).filter(PlantaModel.id == planta_id).first()

    @staticmethod
    def _para_entidade(modelo: PlantaModel) -> Planta:
        return Planta(
            id           = modelo.id,
            nome         = modelo.nome,
            tipo         = modelo.tipo,
            data_plantio = modelo.data_plantio,
            foto_url     = modelo.foto_url,
        )
