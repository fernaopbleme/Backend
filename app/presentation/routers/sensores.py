from fastapi import APIRouter, Depends

from app.application.use_cases.obter_alertas import ObterAlertas
from app.application.use_cases.obter_ultima_leitura import ObterUltimaLeitura
from app.presentation.deps import get_obter_alertas, get_obter_ultima_leitura

router = APIRouter(tags=["Sensores"])


@router.get("/dados")
def get_dados(caso_de_uso: ObterUltimaLeitura = Depends(get_obter_ultima_leitura)):
    avaliada = caso_de_uso.executar()
    return {
        "dados":      avaliada.leitura.bruto,
        "alertas":    avaliada.alertas,
        "recebidoEm": avaliada.leitura.recebido_em.isoformat(),
    }


@router.get("/alertas")
def get_alertas(caso_de_uso: ObterAlertas = Depends(get_obter_alertas)):
    return {"alertas": caso_de_uso.executar()}
