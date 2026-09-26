import asyncio
import logging
from typing import Any, Dict, List, Optional

from fastapi import WebSocket

from app.application.ports.notificador import Notificador

logger = logging.getLogger(__name__)


class WebSocketNotificador(Notificador):
    def __init__(self):
        self._clientes: List[WebSocket] = []
        self._event_loop: Optional[asyncio.AbstractEventLoop] = None

    def definir_event_loop(self, loop: asyncio.AbstractEventLoop) -> None:
        self._event_loop = loop

    def registrar(self, websocket: WebSocket) -> None:
        self._clientes.append(websocket)

    def remover(self, websocket: WebSocket) -> None:
        if websocket in self._clientes:
            self._clientes.remove(websocket)

    def notificar(self, payload: Dict[str, Any]) -> None:
        if self._event_loop is None:
            return
        asyncio.run_coroutine_threadsafe(self._transmitir(payload), self._event_loop)

    async def _transmitir(self, payload: Dict[str, Any]) -> None:
        desconectados = []
        for websocket in list(self._clientes):
            try:
                await websocket.send_json(payload)
            except Exception:
                desconectados.append(websocket)
        for websocket in desconectados:
            self.remover(websocket)
