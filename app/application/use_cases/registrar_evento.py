import logging
from datetime import datetime

from app.domain.entities.evento import Evento
from app.domain.repositories.evento_repository import EventoRepository
from app.domain.services.validador_evento import ValidadorDeEvento

logger = logging.getLogger(__name__)


class RegistrarEvento:
    def __init__(self, repositorio: EventoRepository, validador: ValidadorDeEvento):
        self._repositorio = repositorio
        self._validador = validador

    def executar(self, nome: str, pagina: str, sessao: str) -> Evento:
        self._validador.validar_evento(nome, pagina, sessao)
        evento = self._repositorio.registrar_evento(
            Evento(nome=nome, pagina=pagina, sessao=sessao, criado_em=datetime.now())
        )
        logger.info("Evento registrado: %s em %s", nome, pagina)
        return evento
