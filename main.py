import asyncio
import json
import os
import uuid
import aiofiles
from datetime import datetime
from typing import List, Dict, Any, Optional

import paho.mqtt.client as mqtt
from fastapi import FastAPI, Request, HTTPException, File, UploadFile, Depends, Form
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from fastapi import WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from database import PlantaDB, get_db, Base, engine

# ── Configuração MQTT ─────────────────────
BROKER    = "47d5de0ce14d4654a95021e273720719.s1.eu.hivemq.cloud"
PORT      = 8883
MQTT_USER = "Hidro"
MQTT_PASS = "Hidro123"

# ── Tópicos ───────────────────────────────
TOPIC_SENSORES      = "hidroponia/sensores"
TOPIC_MOTOR_COMANDO = "hidroponia/motor/comando"
TOPIC_MOTOR_STATUS  = "hidroponia/motor/status"

# ─────────────────────────────────────────
event_loop = None

# ── Estado global ─────────────────────────
ultimo_dado         = None
ultimos_alertas     = []
ultimo_motor_status = {}

# ── Thresholds ────────────────────────────
thresholds = {
    "phMin":                  5.5,
    "phMax":                  6.5,
    "ecMin":                  0.8,
    "ecMax":                  1.8,
    "temperaturaAguaMax":     28,
    "temperaturaAmbienteMax": 32,
    "umidadeRelativaMin":     45,
    "nivelAguaMin":           35,
}

# ── WebSocket clients ─────────────────────
clientes_websocket: List[WebSocket] = []

# =============================================
# MQTT Client
# =============================================
mqtt_client = mqtt.Client()
mqtt_client.username_pw_set(MQTT_USER, MQTT_PASS)
mqtt_client.tls_set()

# =============================================
# Helper — Publica comando no MQTT
# =============================================
def _publicar_comando(comando: dict):
    payload = json.dumps(comando)
    result  = mqtt_client.publish(TOPIC_MOTOR_COMANDO, payload, qos=1)
    if result.rc != mqtt.MQTT_ERR_SUCCESS:
        raise HTTPException(
            status_code=502,
            detail=f"Falha ao publicar no MQTT. Código: {result.rc}"
        )
    print(f"✔ Publicado [{TOPIC_MOTOR_COMANDO}]: {payload}")

# =============================================
# Processa alertas
# =============================================
def processar_dados(dados: Dict[str, Any]) -> List[str]:
    alertas = []
    if dados.get("ph") is not None:
        if dados["ph"] < thresholds["phMin"]:
            alertas.append(f"pH abaixo do limite: {dados['ph']}")
        if dados["ph"] > thresholds["phMax"]:
            alertas.append(f"pH acima do limite: {dados['ph']}")
    if dados.get("ec") is not None:
        if dados["ec"] < thresholds["ecMin"]:
            alertas.append(f"EC abaixo do limite: {dados['ec']}")
        if dados["ec"] > thresholds["ecMax"]:
            alertas.append(f"EC acima do limite: {dados['ec']}")
    if dados.get("temperaturaAgua") is not None:
        if dados["temperaturaAgua"] > thresholds["temperaturaAguaMax"]:
            alertas.append(f"Temperatura da água alta: {dados['temperaturaAgua']}°C")
    if dados.get("temperaturaAmbiente") is not None:
        if dados["temperaturaAmbiente"] > thresholds["temperaturaAmbienteMax"]:
            alertas.append(f"Temperatura ambiente alta: {dados['temperaturaAmbiente']}°C")
    if dados.get("umidadeRelativa") is not None:
        if dados["umidadeRelativa"] < thresholds["umidadeRelativaMin"]:
            alertas.append(f"Umidade relativa baixa: {dados['umidadeRelativa']}%")
    if dados.get("nivelAgua") is not None:
        if dados["nivelAgua"] < thresholds["nivelAguaMin"]:
            alertas.append(f"Nível de água baixo: {dados['nivelAgua']}%")
    return alertas

# =============================================
# Envia dados para Flutter via WebSocket
# =============================================
async def enviar_para_flutter(payload):
    clientes_desconectados = []
    for websocket in clientes_websocket:
        try:
            await websocket.send_json(payload)
        except Exception:
            clientes_desconectados.append(websocket)
    for websocket in clientes_desconectados:
        if websocket in clientes_websocket:
            clientes_websocket.remove(websocket)

# =============================================
# Callbacks MQTT
# =============================================
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ Backend conectado ao broker MQTT.")
        client.subscribe(TOPIC_SENSORES)
        client.subscribe(TOPIC_MOTOR_STATUS)
        print(f"✅ Inscrito em: {TOPIC_SENSORES}, {TOPIC_MOTOR_STATUS}")
    else:
        print(f"⚠ Erro ao conectar no MQTT. Código: {rc}")

def on_message(client, userdata, msg):
    global ultimo_dado, ultimos_alertas, ultimo_motor_status
    try:
        dados = json.loads(msg.payload.decode("utf-8"))
        if msg.topic == TOPIC_SENSORES:
            alertas = processar_dados(dados)
            ultimo_dado = {
                "dados":      dados,
                "alertas":    alertas,
                "recebidoEm": datetime.now().isoformat()
            }
            ultimos_alertas = alertas
            print(f"📩 Sensores: {dados}")
            if event_loop is not None:
                asyncio.run_coroutine_threadsafe(
                    enviar_para_flutter(ultimo_dado), event_loop
                )
        elif msg.topic == TOPIC_MOTOR_STATUS:
            ultimo_motor_status = {
                **dados,
                "recebidoEm": datetime.now().isoformat()
            }
            print(f"📩 Motor status: {dados}")
            if event_loop is not None:
                asyncio.run_coroutine_threadsafe(
                    enviar_para_flutter({"motorStatus": ultimo_motor_status}),
                    event_loop
                )
    except Exception as e:
        print(f"⚠ Erro ao processar mensagem MQTT: {e}")

def on_disconnect(client, userdata, rc):
    print(f"⚠ MQTT desconectado! Código: {rc}")

mqtt_client.on_connect    = on_connect
mqtt_client.on_message    = on_message
mqtt_client.on_disconnect = on_disconnect

# =============================================
# Lifespan — cria pasta E monta static aqui!
# =============================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    global event_loop
    event_loop = asyncio.get_running_loop()

    # 1. Cria pasta de fotos se não existir
    os.makedirs("static/fotos", exist_ok=True)

    # 2. Monta arquivos estáticos APÓS garantir que a pasta existe
    app.mount("/static", StaticFiles(directory="static"), name="static")

    # 3. Cria tabelas do banco
    Base.metadata.create_all(bind=engine)

    # 4. Conecta MQTT
    print("Iniciando conexão MQTT...")
    mqtt_client.connect(BROKER, PORT, 60)
    mqtt_client.loop_start()

    yield

    print("Encerrando conexão MQTT...")
    mqtt_client.loop_stop()
    mqtt_client.disconnect()

# ── Cria o app ────────────────────────────
app = FastAPI(lifespan=lifespan)

# =============================================
# CORS Middleware
# =============================================
@app.middleware("http")
async def cors_middleware(request: Request, call_next):
    if request.method == "OPTIONS":
        response = Response()
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "*"
        response.headers["Access-Control-Allow-Headers"] = "*"
        return response
    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response

# =============================================
# Models
# =============================================
class ComandoCiclo(BaseModel):
    minutos_ligado: int = Field(
        ..., ge=1, le=1440,
        description="Minutos que a bomba fica LIGADA por ciclo"
    )
    minutos_desligado: int = Field(
        ..., ge=1, le=1440,
        description="Minutos que a bomba fica DESLIGADA por ciclo"
    )

class PlantaResponse(BaseModel):
    id:           int
    nome:         str
    tipo:         str
    data_plantio: str
    foto_url:     Optional[str] = None

    class Config:
        from_attributes = True

# =============================================
# WebSocket
# =============================================
@app.websocket("/ws/sensores")
async def websocket_sensores(websocket: WebSocket):
    await websocket.accept()
    clientes_websocket.append(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        clientes_websocket.remove(websocket)

# =============================================
# Rotas — Geral
# =============================================
@app.get("/")
def home():
    return {
        "message":   "Backend Hidropônica rodando",
        "mqttTopic": TOPIC_SENSORES
    }

# =============================================
# Rotas — Sensores
# =============================================
@app.get("/dados")
def get_dados():
    if not ultimo_dado:
        raise HTTPException(status_code=503, detail="Nenhum dado recebido ainda.")
    return ultimo_dado

@app.get("/alertas")
def get_alertas():
    return {"alertas": ultimos_alertas}

# =============================================
# Rotas — Thresholds
# =============================================
@app.get("/thresholds")
def get_thresholds():
    return thresholds

@app.post("/thresholds")
def atualizar_thresholds(novos_thresholds: Dict[str, float]):
    thresholds.update(novos_thresholds)
    return {
        "message":    "Thresholds atualizados com sucesso",
        "thresholds": thresholds
    }

# =============================================
# Rotas — Motor
# =============================================
@app.post("/motor/ciclo", summary="Inicia ciclo automático da bomba")
def iniciar_ciclo(body: ComandoCiclo):
    comando = {
        "acao":              "ciclo",
        "minutos_ligado":    body.minutos_ligado,
        "minutos_desligado": body.minutos_desligado
    }
    _publicar_comando(comando)
    return {
        "sucesso":  True,
        "mensagem": f"Ciclo iniciado: {body.minutos_ligado} min ligado / {body.minutos_desligado} min desligado",
        "comando":  comando
    }

@app.post("/motor/desligar", summary="Para o motor imediatamente")
def desligar_motor():
    comando = {"acao": "desligar"}
    _publicar_comando(comando)
    return {
        "sucesso":  True,
        "mensagem": "Motor desligado",
        "comando":  comando
    }

@app.get("/motor/status", summary="Último status do motor")
def get_motor_status():
    if not ultimo_motor_status:
        raise HTTPException(status_code=503, detail="Nenhum status do motor recebido ainda.")
    return ultimo_motor_status

# =============================================
# Rotas — Plantas
# =============================================
@app.get(
    "/plantas",
    response_model=list[PlantaResponse],
    summary="Lista todas as plantas"
)
def listar_plantas(db: Session = Depends(get_db)):
    return db.query(PlantaDB).all()

@app.post(
    "/plantas",
    response_model=PlantaResponse,
    status_code=201,
    summary="Cadastra uma nova planta"
)
async def criar_planta(
    nome:         str        = Form(...),
    tipo:         str        = Form(...),
    data_plantio: str        = Form(...),
    foto:         UploadFile = File(None),
    db:           Session    = Depends(get_db)
):
    foto_url = None
    if foto and foto.filename:
        extensao = foto.filename.split(".")[-1].lower()
        if extensao not in ["jpg", "jpeg", "png", "webp"]:
            raise HTTPException(
                status_code=400,
                detail="Formato inválido. Use jpg, jpeg, png ou webp."
            )
        nome_arquivo = f"{uuid.uuid4()}.{extensao}"
        caminho      = f"static/fotos/{nome_arquivo}"
        async with aiofiles.open(caminho, "wb") as f:
            await f.write(await foto.read())
        foto_url = f"/static/fotos/{nome_arquivo}"

    planta = PlantaDB(
        nome         = nome,
        tipo         = tipo,
        data_plantio = data_plantio,
        foto_url     = foto_url
    )
    db.add(planta)
    db.commit()
    db.refresh(planta)
    print(f"🌱 Planta cadastrada: {nome} ({tipo})")
    return planta

@app.delete(
    "/plantas/{planta_id}",
    summary="Remove uma planta"
)
def deletar_planta(planta_id: int, db: Session = Depends(get_db)):
    planta = db.query(PlantaDB).filter(PlantaDB.id == planta_id).first()
    if not planta:
        raise HTTPException(
            status_code=404,
            detail=f"Planta {planta_id} não encontrada."
        )
    if planta.foto_url:
        caminho = planta.foto_url.lstrip("/")
        if os.path.exists(caminho):
            os.remove(caminho)
    db.delete(planta)
    db.commit()
    print(f"🗑 Planta removida: {planta.nome}")
    return {
        "sucesso":  True,
        "mensagem": f"Planta '{planta.nome}' removida com sucesso"
    }

@app.get(
    "/plantas/{planta_id}",
    response_model=PlantaResponse,
    summary="Busca planta por ID"
)
def buscar_planta(planta_id: int, db: Session = Depends(get_db)):
    planta = db.query(PlantaDB).filter(PlantaDB.id == planta_id).first()
    if not planta:
        raise HTTPException(
            status_code=404,
            detail=f"Planta {planta_id} não encontrada."
        )
    return planta