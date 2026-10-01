from fastapi import APIRouter

from app.core.config import TOPIC_SENSORES

router = APIRouter(tags=["Geral"])


@router.get("/")
def home():
    return {
        "message":   "Backend Hidropônica rodando",
        "mqttTopic": TOPIC_SENSORES
    }
