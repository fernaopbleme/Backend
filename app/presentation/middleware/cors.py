from fastapi import FastAPI, Request
from fastapi.responses import Response


def registrar_cors(app: FastAPI) -> None:
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
