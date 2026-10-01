from dataclasses import dataclass, fields
from typing import Any, Dict


@dataclass
class Thresholds:
    ph_min: float = 5.5
    ph_max: float = 6.5
    ec_min: float = 0.8
    ec_max: float = 1.8
    temperatura_agua_max: float = 28
    temperatura_ambiente_max: float = 32
    umidade_relativa_min: float = 45
    nivel_agua_min: float = 35

    _APELIDOS = {
        "ph_min":                  "phMin",
        "ph_max":                  "phMax",
        "ec_min":                  "ecMin",
        "ec_max":                  "ecMax",
        "temperatura_agua_max":    "temperaturaAguaMax",
        "temperatura_ambiente_max": "temperaturaAmbienteMax",
        "umidade_relativa_min":    "umidadeRelativaMin",
        "nivel_agua_min":          "nivelAguaMin",
    }

    def to_dict(self) -> Dict[str, float]:
        return {self._APELIDOS[f.name]: getattr(self, f.name) for f in fields(self)}

    def aplicar(self, valores: Dict[str, Any]) -> None:
        por_apelido = {apelido: nome for nome, apelido in self._APELIDOS.items()}
        for apelido, valor in valores.items():
            nome = por_apelido.get(apelido)
            if nome is not None and valor is not None:
                setattr(self, nome, valor)
