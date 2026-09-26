import re

from app.domain.exceptions import EmailInvalido, EventoInvalido

# Nomes de CTA que a loja pode registrar. Lista fechada de propósito:
# sem isso qualquer um poderia encher a tabela com lixo, e o resumo da
# validação deixaria de significar alguma coisa.
EVENTOS_ACEITOS = {
    "cta_diy",
    "cta_interesse",
    "cta_ver_produtos",
    "cta_ver_guias",
    "cta_montar_torre",
    "cta_ver_kits",
    "cta_add_carrinho",
    "cta_entrar_painel",
    "pagina_vista",
}

_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]{2,}$")

_LIMITE_TEXTO = 200


class ValidadorDeEvento:
    def validar_evento(self, nome: str, pagina: str, sessao: str) -> None:
        if nome not in EVENTOS_ACEITOS:
            raise EventoInvalido(f"Evento desconhecido: {nome}")
        if not sessao or len(sessao) > _LIMITE_TEXTO:
            raise EventoInvalido("Sessão ausente ou longa demais.")
        if len(pagina) > _LIMITE_TEXTO:
            raise EventoInvalido("Página longa demais.")

    def validar_interesse(self, email: str, produto: str, sessao: str) -> str:
        email_limpo = email.strip().lower()
        if not _EMAIL.match(email_limpo) or len(email_limpo) > _LIMITE_TEXTO:
            raise EmailInvalido(email)
        if not produto or len(produto) > _LIMITE_TEXTO:
            raise EventoInvalido("Produto ausente ou longo demais.")
        if not sessao or len(sessao) > _LIMITE_TEXTO:
            raise EventoInvalido("Sessão ausente ou longa demais.")
        return email_limpo
