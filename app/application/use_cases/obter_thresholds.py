from app.application.ports.estado_monitoramento import EstadoDeMonitoramento
from app.domain.entities.thresholds import Thresholds


class ObterThresholds:
    def __init__(self, estado: EstadoDeMonitoramento):
        self._estado = estado

    def executar(self) -> Thresholds:
        return self._estado.thresholds()
