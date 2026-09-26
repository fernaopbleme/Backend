from app.application.ports.estado_monitoramento import EstadoDeMonitoramento
from app.domain.entities.leitura import LeituraAvaliada
from app.domain.exceptions import NenhumDadoDisponivel


class ObterUltimaLeitura:
    def __init__(self, estado: EstadoDeMonitoramento):
        self._estado = estado

    def executar(self) -> LeituraAvaliada:
        leitura = self._estado.ultima_leitura()
        if leitura is None:
            raise NenhumDadoDisponivel("Nenhum dado recebido ainda.")
        return leitura
