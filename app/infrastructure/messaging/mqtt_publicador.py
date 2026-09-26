import json
import logging

import paho.mqtt.client as mqtt

from app.application.ports.publicador_comandos import PublicadorDeComandos
from app.core.config import TOPIC_MOTOR_COMANDO
from app.domain.entities.leitura import ComandoMotor
from app.domain.exceptions import FalhaNaPublicacao

logger = logging.getLogger(__name__)


class MqttPublicador(PublicadorDeComandos):
    def __init__(self, cliente: mqtt.Client):
        self._cliente = cliente

    def publicar(self, comando: ComandoMotor) -> None:
        payload = json.dumps(comando.to_payload())
        resultado = self._cliente.publish(TOPIC_MOTOR_COMANDO, payload, qos=1)
        if resultado.rc != mqtt.MQTT_ERR_SUCCESS:
            raise FalhaNaPublicacao(resultado.rc)
        logger.info("Publicado [%s]: %s", TOPIC_MOTOR_COMANDO, payload)
