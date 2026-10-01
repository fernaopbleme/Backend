from typing import List

from app.domain.entities.leitura import LeituraSensores
from app.domain.entities.thresholds import Thresholds


class AvaliadorDeAlertas:
    def avaliar(self, leitura: LeituraSensores, thresholds: Thresholds) -> List[str]:
        alertas: List[str] = []

        if leitura.ph is not None:
            if leitura.ph < thresholds.ph_min:
                alertas.append(f"pH abaixo do limite: {leitura.ph}")
            if leitura.ph > thresholds.ph_max:
                alertas.append(f"pH acima do limite: {leitura.ph}")

        if leitura.ec is not None:
            if leitura.ec < thresholds.ec_min:
                alertas.append(f"EC abaixo do limite: {leitura.ec}")
            if leitura.ec > thresholds.ec_max:
                alertas.append(f"EC acima do limite: {leitura.ec}")

        if leitura.temperatura_agua is not None:
            if leitura.temperatura_agua > thresholds.temperatura_agua_max:
                alertas.append(f"Temperatura da água alta: {leitura.temperatura_agua}°C")

        if leitura.temperatura_ambiente is not None:
            if leitura.temperatura_ambiente > thresholds.temperatura_ambiente_max:
                alertas.append(f"Temperatura ambiente alta: {leitura.temperatura_ambiente}°C")

        if leitura.umidade_relativa is not None:
            if leitura.umidade_relativa < thresholds.umidade_relativa_min:
                alertas.append(f"Umidade relativa baixa: {leitura.umidade_relativa}%")

        if leitura.nivel_agua is not None:
            if leitura.nivel_agua < thresholds.nivel_agua_min:
                alertas.append(f"Nível de água baixo: {leitura.nivel_agua}%")

        return alertas
