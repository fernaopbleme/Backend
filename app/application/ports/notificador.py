from abc import ABC, abstractmethod
from typing import Any, Dict


class Notificador(ABC):
    @abstractmethod
    def notificar(self, payload: Dict[str, Any]) -> None:
        ...
