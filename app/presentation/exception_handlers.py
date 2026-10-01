from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.domain.exceptions import (
    EmailInvalido,
    EventoInvalido,
    FalhaNaPublicacao,
    FormatoDeFotoInvalido,
    NenhumDadoDisponivel,
    PlantaNaoEncontrada,
)

_STATUS_POR_EXCECAO = {
    PlantaNaoEncontrada:  404,
    FormatoDeFotoInvalido: 400,
    EmailInvalido:         422,
    EventoInvalido:        422,
    NenhumDadoDisponivel: 503,
    FalhaNaPublicacao:    502,
}


def registrar_handlers(app: FastAPI) -> None:
    for excecao, status in _STATUS_POR_EXCECAO.items():
        app.add_exception_handler(excecao, _criar_handler(status))


def _criar_handler(status: int):
    async def handler(request: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(status_code=status, content={"detail": str(exc)})
    return handler
