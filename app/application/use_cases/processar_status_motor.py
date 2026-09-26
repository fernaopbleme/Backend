import logging
from datetime import datetime
from typing import Any, Dict

from app.application.ports.estado_monitoramento import EstadoDeMonitoramento
from app.application.ports.notificador import Notificador
from app.domain.entities.leitura import StatusMotor

logger = logging.getLogger(__name__)


class ProcessarStatusMotor:
    def __init__(self, estado: EstadoDeMonitoramento, notificador: Notificador):
        self._estado = estado
        self._notificador = notificador

    def executar(self, dados: Dict[str, Any]) -> StatusMotor:
        status = StatusMotor(bruto=dados, recebido_em=datetime.now())
        self._estado.salvar_status_motor(status)
        logger.info("Motor status: %s", dados)

        self._notificador.notificar({
            "motorStatus": {**status.bruto, "recebidoEm": status.recebido_em.isoformat()}
        })
        return status
