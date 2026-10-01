from abc import ABC, abstractmethod

from app.domain.entities.leitura import ComandoMotor


class PublicadorDeComandos(ABC):
    @abstractmethod
    def publicar(self, comando: ComandoMotor) -> None:
        ...
