import logging
import os
import uuid
from typing import List, Optional

import aiofiles

from app.application.ports.armazenamento_fotos import ArmazenamentoDeFotos
from app.core.config import DIRETORIO_FOTOS, EXTENSOES_ACEITAS, URL_FOTOS

logger = logging.getLogger(__name__)


class FilesystemFotoStorage(ArmazenamentoDeFotos):
    def extensoes_aceitas(self) -> List[str]:
        return EXTENSOES_ACEITAS

    async def salvar(self, conteudo: bytes, extensao: str) -> str:
        os.makedirs(DIRETORIO_FOTOS, exist_ok=True)
        nome_arquivo = f"{uuid.uuid4()}.{extensao}"
        caminho = os.path.join(DIRETORIO_FOTOS, nome_arquivo)
        async with aiofiles.open(caminho, "wb") as arquivo:
            await arquivo.write(conteudo)
        return f"{URL_FOTOS}/{nome_arquivo}"

    def remover(self, foto_url: Optional[str]) -> None:
        if not foto_url:
            return
        caminho = foto_url.lstrip("/")
        try:
            if os.path.exists(caminho):
                os.remove(caminho)
        except OSError:
            logger.warning("Não foi possível remover a foto %s", caminho, exc_info=True)
