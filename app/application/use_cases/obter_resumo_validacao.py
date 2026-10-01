from typing import List

from app.domain.entities.evento import Evento, Interesse, ResumoValidacao
from app.domain.repositories.evento_repository import EventoRepository


class ObterResumoValidacao:
    def __init__(self, repositorio: EventoRepository):
        self._repositorio = repositorio

    def executar(self) -> ResumoValidacao:
        return self._repositorio.resumo()


class ListarInteresses:
    def __init__(self, repositorio: EventoRepository):
        self._repositorio = repositorio

    def executar(self) -> List[Interesse]:
        return self._repositorio.listar_interesses()


class ExportarEventos:
    """Linhas cruas, para somar sessões corretamente depois.

    O resumo já vem agregado: somar `sessoes` de dois resumos conta duas
    vezes quem visitou nas duas janelas. Com as linhas cruas dá para
    remover a duplicata pelo id de sessão.
    """

    def __init__(self, repositorio: EventoRepository):
        self._repositorio = repositorio

    def executar(self) -> List[Evento]:
        return self._repositorio.listar_eventos()
