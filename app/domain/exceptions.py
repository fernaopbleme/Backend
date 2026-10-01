class ErroDeDominio(Exception):
    pass


class PlantaNaoEncontrada(ErroDeDominio):
    def __init__(self, planta_id: int):
        self.planta_id = planta_id
        super().__init__(f"Planta {planta_id} não encontrada.")


class FormatoDeFotoInvalido(ErroDeDominio):
    def __init__(self, extensoes_aceitas):
        self.extensoes_aceitas = extensoes_aceitas
        super().__init__("Formato inválido. Use jpg, jpeg, png ou webp.")


class NenhumDadoDisponivel(ErroDeDominio):
    def __init__(self, mensagem: str):
        super().__init__(mensagem)


class FalhaNaPublicacao(ErroDeDominio):
    def __init__(self, codigo: int):
        self.codigo = codigo
        super().__init__(f"Falha ao publicar no MQTT. Código: {codigo}")


class EmailInvalido(ErroDeDominio):
    def __init__(self, email: str):
        self.email = email
        super().__init__(f"E-mail inválido: {email}")


class EventoInvalido(ErroDeDominio):
    def __init__(self, motivo: str):
        super().__init__(motivo)
