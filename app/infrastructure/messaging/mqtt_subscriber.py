import json
import logging

import paho.mqtt.client as mqtt

from app.application.use_cases.processar_leitura import ProcessarLeitura
from app.application.use_cases.processar_status_motor import ProcessarStatusMotor
from app.core.config import TOPIC_MOTOR_STATUS, TOPIC_SENSORES

logger = logging.getLogger(__name__)


class MqttSubscriber:
    def __init__(
        self,
        cliente: mqtt.Client,
        processar_leitura: ProcessarLeitura,
        processar_status_motor: ProcessarStatusMotor,
    ):
        self._cliente = cliente
        self._processar_leitura = processar_leitura
        self._processar_status_motor = processar_status_motor

    def registrar(self) -> None:
        self._cliente.on_connect = self._on_connect
        self._cliente.on_message = self._on_message
        self._cliente.on_disconnect = self._on_disconnect

    def _on_connect(self, cliente, userdata, flags, rc):
        if rc == 0:
            logger.info("Backend conectado ao broker MQTT.")
            cliente.subscribe(TOPIC_SENSORES)
            cliente.subscribe(TOPIC_MOTOR_STATUS)
            logger.info("Inscrito em: %s, %s", TOPIC_SENSORES, TOPIC_MOTOR_STATUS)
        else:
            logger.error("Erro ao conectar no MQTT. Código: %s", rc)

    def _on_message(self, cliente, userdata, msg):
        try:
            dados = json.loads(msg.payload.decode("utf-8"))
        except (ValueError, UnicodeDecodeError):
            logger.warning("Payload MQTT inválido em %s", msg.topic, exc_info=True)
            return

        try:
            if msg.topic == TOPIC_SENSORES:
                self._processar_leitura.executar(dados)
            elif msg.topic == TOPIC_MOTOR_STATUS:
                self._processar_status_motor.executar(dados)
        except Exception:
            logger.error("Erro ao processar mensagem MQTT de %s", msg.topic, exc_info=True)

    def _on_disconnect(self, cliente, userdata, rc):
        logger.warning("MQTT desconectado! Código: %s", rc)
