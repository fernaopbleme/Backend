import logging
from datetime import datetime

from app.domain.entities.evento import Interesse
from app.domain.repositories.evento_repository import EventoRepository
from app.domain.services.validador_evento import ValidadorDeEvento

logger = logging.getLogger(__name__)


class RegistrarInteresse:
    def __init__(self, repositorio: EventoRepository, validador: ValidadorDeEvento):
        self._repositorio = repositorio
        self._validador = validador

    def executar(self, email: str, produto: str, sessao: str) -> Interesse:
        email_limpo = self._validador.validar_interesse(email, produto, sessao)
        interesse = self._repositorio.registrar_interesse(
            Interesse(
                email=email_limpo,
                produto=produto,
                sessao=sessao,
                criado_em=datetime.now(),
            )
        )
        logger.info("Interesse registrado para o produto %s", produto)
        return interesse
