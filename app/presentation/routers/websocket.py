from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect

from app.infrastructure.notifications.websocket_notificador import WebSocketNotificador
from app.presentation.deps import get_notificador

router = APIRouter()


@router.websocket("/ws/sensores")
async def websocket_sensores(
    websocket: WebSocket,
    notificador: WebSocketNotificador = Depends(get_notificador),
):
    await websocket.accept()
    notificador.registrar(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        notificador.remover(websocket)
