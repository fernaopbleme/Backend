from typing import List

from sqlalchemy import distinct, func
from sqlalchemy.orm import Session

from app.domain.entities.evento import (
    ContagemEvento,
    Evento,
    Interesse,
    ResumoValidacao,
)
from app.domain.repositories.evento_repository import EventoRepository
from app.infrastructure.persistence.models import EventoModel, InteresseModel


class SqlAlchemyEventoRepository(EventoRepository):
    def __init__(self, session: Session):
        self._session = session

    def registrar_evento(self, evento: Evento) -> Evento:
        modelo = EventoModel(
            nome      = evento.nome,
            pagina    = evento.pagina,
            sessao    = evento.sessao,
            criado_em = evento.criado_em,
        )
        self._session.add(modelo)
        self._session.commit()
        self._session.refresh(modelo)
        return self._evento(modelo)

    def registrar_interesse(self, interesse: Interesse) -> Interesse:
        modelo = InteresseModel(
            email     = interesse.email,
            produto   = interesse.produto,
            sessao    = interesse.sessao,
            criado_em = interesse.criado_em,
        )
        self._session.add(modelo)
        self._session.commit()
        self._session.refresh(modelo)
        return self._interesse(modelo)

    def resumo(self) -> ResumoValidacao:
        # Total de cliques e de sessões distintas por CTA: um visitante que
        # clica cinco vezes conta como 5 cliques e 1 sessão.
        linhas = (
            self._session.query(
                EventoModel.nome,
                func.count(EventoModel.id),
                func.count(distinct(EventoModel.sessao)),
            )
            .group_by(EventoModel.nome)
            .all()
        )

        contagens = [
            ContagemEvento(nome=nome, total=total, sessoes=sessoes)
            for nome, total, sessoes in linhas
        ]
        contagens.sort(key=lambda c: c.total, reverse=True)

        total_interesses = self._session.query(func.count(InteresseModel.id)).scalar() or 0
        total_sessoes = (
            self._session.query(func.count(distinct(EventoModel.sessao))).scalar() or 0
        )

        return ResumoValidacao(
            eventos=contagens,
            total_interesses=total_interesses,
            total_sessoes=total_sessoes,
        )

    def listar_interesses(self) -> List[Interesse]:
        modelos = (
            self._session.query(InteresseModel)
            .order_by(InteresseModel.criado_em.desc())
            .all()
        )
        return [self._interesse(m) for m in modelos]

    def listar_eventos(self) -> List[Evento]:
        modelos = (
            self._session.query(EventoModel)
            .order_by(EventoModel.criado_em.asc())
            .all()
        )
        return [self._evento(m) for m in modelos]

    @staticmethod
    def _evento(modelo: EventoModel) -> Evento:
        return Evento(
            id        = modelo.id,
            nome      = modelo.nome,
            pagina    = modelo.pagina,
            sessao    = modelo.sessao,
            criado_em = modelo.criado_em,
        )

    @staticmethod
    def _interesse(modelo: InteresseModel) -> Interesse:
        return Interesse(
            id        = modelo.id,
            email     = modelo.email,
            produto   = modelo.produto,
            sessao    = modelo.sessao,
            criado_em = modelo.criado_em,
        )
