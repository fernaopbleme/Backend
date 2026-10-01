from abc import ABC, abstractmethod
from typing import List

from app.domain.entities.evento import (
    Evento,
    Interesse,
    ResumoValidacao,
)


class EventoRepository(ABC):
    @abstractmethod
    def registrar_evento(self, evento: Evento) -> Evento:
        ...

    @abstractmethod
    def registrar_interesse(self, interesse: Interesse) -> Interesse:
        ...

    @abstractmethod
    def resumo(self) -> ResumoValidacao:
        ...

    @abstractmethod
    def listar_interesses(self) -> List[Interesse]:
        ...

    @abstractmethod
    def listar_eventos(self) -> List[Evento]:
        ...
