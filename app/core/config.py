import os

# ── MQTT ──────────────────────────────────
BROKER    = os.getenv("MQTT_BROKER", "47d5de0ce14d4654a95021e273720719.s1.eu.hivemq.cloud")
PORT      = int(os.getenv("MQTT_PORT", "8883"))
MQTT_USER = os.getenv("MQTT_USER", "Hidro")
MQTT_PASS = os.getenv("MQTT_PASS", "Hidro123")

# ── Tópicos ───────────────────────────────
TOPIC_SENSORES      = os.getenv("MQTT_TOPIC_SENSORES", "hidroponia/sensores")
TOPIC_MOTOR_COMANDO = os.getenv("MQTT_TOPIC_MOTOR_COMANDO", "hidroponia/motor/comando")
TOPIC_MOTOR_STATUS  = os.getenv("MQTT_TOPIC_MOTOR_STATUS", "hidroponia/motor/status")

# ── Banco de dados ────────────────────────
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./plantas.db")

# ── Fotos ─────────────────────────────────
DIRETORIO_ESTATICO = "static"
DIRETORIO_FOTOS    = "static/fotos"
URL_FOTOS          = "/static/fotos"
EXTENSOES_ACEITAS  = ["jpg", "jpeg", "png", "webp"]

# ── Log ───────────────────────────────────
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
