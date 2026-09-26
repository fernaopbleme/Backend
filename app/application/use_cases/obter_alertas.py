from typing import List

from app.application.ports.estado_monitoramento import EstadoDeMonitoramento


class ObterAlertas:
    def __init__(self, estado: EstadoDeMonitoramento):
        self._estado = estado

    def executar(self) -> List[str]:
        leitura = self._estado.ultima_leitura()
        return leitura.alertas if leitura is not None else []
