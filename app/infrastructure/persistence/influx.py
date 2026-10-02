import os
from pathlib import Path

from dotenv import load_dotenv
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

BASE_DIR = Path(__file__).resolve().parents[4]
load_dotenv(BASE_DIR / "env.env")

INFLUX_URL = os.getenv("INFLUX_URL", "").strip()
INFLUX_TOKEN = os.getenv("INFLUX_TOKEN", "").strip()
INFLUX_ORG = os.getenv("INFLUX_ORG", "").strip()
INFLUX_BUCKET = os.getenv("INFLUX_BUCKET", "").strip()

if INFLUX_URL and INFLUX_TOKEN and INFLUX_ORG and INFLUX_BUCKET:
    client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
    write_api = client.write_api(write_options=SYNCHRONOUS)
    query_api = client.query_api()
else:
    client = None
    write_api = None
    query_api = None


def _validar_influx():
    if client is None or write_api is None or query_api is None:
        raise RuntimeError(
            "InfluxDB não configurado. Defina INFLUX_URL, INFLUX_TOKEN, INFLUX_ORG e INFLUX_BUCKET no env.env."
        )


def write_sensor_reading(dados: dict, device: str = "hidroponia_01"):
    """Grava uma leitura de sensores no InfluxDB."""
    _validar_influx()
    point = Point("sensor_reading").tag("device", device)

    for campo, valor in dados.items():
        if isinstance(valor, (int, float)):
            point = point.field(campo, valor)

    write_api.write(bucket=INFLUX_BUCKET, record=point)


def get_recent_readings(hours: int = 1):
    _validar_influx()
    query = f'''
    from(bucket: "{INFLUX_BUCKET}")
      |> range(start: -{hours}h)
      |> filter(fn: (r) => r._measurement == "sensor_reading")
    '''
    return query_api.query(query, org=INFLUX_ORG)
