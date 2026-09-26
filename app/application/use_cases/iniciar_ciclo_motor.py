from app.application.ports.publicador_comandos import PublicadorDeComandos
from app.domain.entities.leitura import ComandoMotor


class IniciarCicloMotor:
    def __init__(self, publicador: PublicadorDeComandos):
        self._publicador = publicador

    def executar(self, minutos_ligado: int, minutos_desligado: int) -> ComandoMotor:
        comando = ComandoMotor(
            acao="ciclo",
            minutos_ligado=minutos_ligado,
            minutos_desligado=minutos_desligado,
        )
        self._publicador.publicar(comando)
        return comando
