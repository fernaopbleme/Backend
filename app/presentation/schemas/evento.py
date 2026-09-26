from datetime import datetime
from typing import List

from pydantic import BaseModel, Field


class EventoCreate(BaseModel):
    nome:   str = Field(..., max_length=200, description="Nome do CTA clicado")
    pagina: str = Field("", max_length=200, description="Rota onde o clique aconteceu")
    sessao: str = Field(..., max_length=200, description="Id anônimo do navegador")


class InteresseCreate(BaseModel):
    email:   str = Field(..., max_length=200)
    produto: str = Field(..., max_length=200)
    sessao:  str = Field(..., max_length=200)


class ContagemResponse(BaseModel):
    nome:    str
    total:   int
    sessoes: int


class ResumoResponse(BaseModel):
    eventos:          List[ContagemResponse]
    total_interesses: int
    total_sessoes:    int


class InteresseResponse(BaseModel):
    id:        int
    email:     str
    produto:   str
    criado_em: datetime


class EventoExportResponse(BaseModel):
    """Linha crua, com a sessão, para agregar sem contar ninguém duas vezes."""

    id:        int
    nome:      str
    pagina:    str
    sessao:    str
    criado_em: datetime
