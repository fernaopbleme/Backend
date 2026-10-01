import logging
from datetime import datetime
from typing import Any, Dict

from app.application.ports.estado_monitoramento import EstadoDeMonitoramento
from app.application.ports.notificador import Notificador
from app.domain.entities.leitura import LeituraAvaliada, LeituraSensores
from app.domain.services.avaliador_alertas import AvaliadorDeAlertas

logger = logging.getLogger(__name__)


class ProcessarLeitura:
    def __init__(
        self,
        estado: EstadoDeMonitoramento,
        avaliador: AvaliadorDeAlertas,
        notificador: Notificador,
    ):
        self._estado = estado
        self._avaliador = avaliador
        self._notificador = notificador

    def executar(self, dados: Dict[str, Any]) -> LeituraAvaliada:
        leitura = LeituraSensores(bruto=dados, recebido_em=datetime.now())
        alertas = self._avaliador.avaliar(leitura, self._estado.thresholds())
        avaliada = LeituraAvaliada(leitura=leitura, alertas=alertas)

        self._estado.salvar_leitura(avaliada)
        logger.info("Sensores: %s", dados)

        self._notificador.notificar({
            "dados":      leitura.bruto,
            "alertas":    alertas,
            "recebidoEm": leitura.recebido_em.isoformat(),
        })
        return avaliada
