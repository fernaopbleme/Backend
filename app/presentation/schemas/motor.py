from pydantic import BaseModel, Field


class ComandoCiclo(BaseModel):
    minutos_ligado: int = Field(
        ..., ge=1, le=1440,
        description="Minutos que a bomba fica LIGADA por ciclo"
    )
    minutos_desligado: int = Field(
        ..., ge=1, le=1440,
        description="Minutos que a bomba fica DESLIGADA por ciclo"
    )
