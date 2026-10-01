from abc import ABC, abstractmethod
from typing import Optional


class ArmazenamentoDeFotos(ABC):
    @abstractmethod
    async def salvar(self, conteudo: bytes, extensao: str) -> str:
        ...

    @abstractmethod
    def remover(self, foto_url: Optional[str]) -> None:
        ...

    @abstractmethod
    def extensoes_aceitas(self):
        ...
