from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Evento:
    """Um clique registrado na loja, para validar interesse no produto.

    `sessao` é um id anônimo gerado no navegador: serve para separar
    "10 cliques de 1 pessoa" de "10 pessoas", sem identificar ninguém.
    """

    nome: str
    pagina: str
    sessao: str
    criado_em: Optional[datetime] = None
    id: Optional[int] = None


@dataclass
class Interesse:
    """Alguém que deixou o e-mail dizendo qual produto quer.

    Sinal de validação muito mais forte que um clique.
    """

    email: str
    produto: str
    sessao: str
    criado_em: Optional[datetime] = None
    id: Optional[int] = None


@dataclass
class ContagemEvento:
    nome: str
    total: int
    sessoes: int


@dataclass
class ResumoValidacao:
    eventos: list[ContagemEvento]
    total_interesses: int
    total_sessoes: int
