# ============================================

from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import os
from dotenv import load_dotenv

load_dotenv("env.env")

INFLUX_URL    = os.getenv("INFLUX_URL")
INFLUX_TOKEN  = os.getenv("INFLUX_TOKEN")
INFLUX_ORG    = os.getenv("INFLUX_ORG")
INFLUX_BUCKET = os.getenv("INFLUX_BUCKET")

client     = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
write_api  = client.write_api(write_options=SYNCHRONOUS)
query_api  = client.query_api()

def write_sensor_reading(dados: dict, device: str = "hidroponia_01"):
    """Grava uma leitura de sensores no InfluxDB. Aceita qualquer campo numérico do dict."""
    point = Point("sensor_reading").tag("device", device)

    for campo, valor in dados.items():
        if isinstance(valor, (int, float)):
            point = point.field(campo, valor)

    write_api.write(bucket=INFLUX_BUCKET, record=point)

def get_recent_readings(hours: int = 1):
    query = f'''
    from(bucket: "{INFLUX_BUCKET}")
      |> range(start: -{hours}h)
      |> filter(fn: (r) => r._measurement == "sensor_reading")
    '''
    return query_api.query(query, org=INFLUX_ORG)