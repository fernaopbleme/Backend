# Deploy do backend

O codigo serve Azure e Render sem mudanca: tudo que varia esta em variavel
de ambiente.

## Trocar o MQTT sem o seu computador

Sao tres lugares, e o que muda depende do que voce trocou.

| o que mudou | onde trocar | de onde |
|---|---|---|
| **senha / usuario** | App Service > Configuration > Application settings (`MQTT_PASS`, `MQTT_USER`) | portal da Azure, funciona no celular |
| **endereco do broker** | `app/core/config.py`, linha do `BROKER` | editor do GitHub, no navegador |
| idem, no fallback | `render.yaml`, chave `MQTT_BROKER` | idem |

A senha **nao** entra no repositorio. Nao e preciosismo: a antiga esta no
historico publico deste repo desde maio e e por isso que ela tem de ser
trocada. Alem disso o GitHub tem protecao de push que costuma barrar
credencial em diff, entao a tentativa provavelmente falharia no meio.
O campo nas Application settings resolve do celular, no mesmo tempo.

Localmente, o `.env` na raiz cobre usuario e senha (modelo em
`.env.example`). **O simulador de dados tem os valores antigos chumbados e
nao esta em repositorio nenhum** — ao trocar a senha, ele para de conectar
ate ser ajustado na maquina onde ele vive.

## Azure App Service — plano F1 (gratuito)

Escolha consciente para a fase de teste. O que vem junto:

* **Sem Always On.** O App Service descarrega a aplicacao depois de ~20 min
  sem acesso HTTP, e com ela morre a conexao MQTT — leitura publicada
  enquanto dorme nao e gravada, sem erro aparecer em lugar nenhum. Nao da
  para coletar dado continuamente no F1.
* **5 conexoes WebSocket simultaneas** (B1 sobe para 350). Um painel aberto
  por pessoa; numa banca isso basta, numa feira nao.
* **60 min de CPU por dia.** Na pratica nao incomoda justamente porque a
  aplicacao dorme.

Antes de apresentar, nesta ordem:

1. abrir a URL do backend no navegador e esperar responder (primeiro acesso
   leva ~30-60s, e o que acorda a aplicacao e reconecta o MQTT);
2. so entao iniciar o simulador — se ele publicar antes, o dado se perde;
3. abrir o painel.

```bash
GRUPO=aerotower-rg
APP=aerotower-backend          # tem de ser unico no .azurewebsites.net
REGIAO=eastus

az group create --name $GRUPO --location $REGIAO

az appservice plan create --name aerotower-plan --resource-group $GRUPO \
  --sku F1 --is-linux

az webapp create --name $APP --resource-group $GRUPO \
  --plan aerotower-plan --runtime "PYTHON:3.11"

# --always-on NAO entra aqui: o F1 nao suporta, e o comando falha.
# Um processo so: ver o cabecalho de startup.sh para o porque.
az webapp config set --name $APP --resource-group $GRUPO \
  --startup-file startup.sh \
  --web-sockets-enabled true

# Sem --web-sockets-enabled o /ws/sensores nao conecta, e falha de um jeito
# que parece problema de CORS no navegador.

az webapp config appsettings set --name $APP --resource-group $GRUPO \
  --settings \
    SCM_DO_BUILD_DURING_DEPLOYMENT=true \
    MQTT_USER="<usuario do hivemq>" \
    MQTT_PASS="<senha nova do hivemq>" \
    DATABASE_URL="sqlite:////home/data/plantas.db"
```

`/home` persiste entre reinicios; `/home/site/wwwroot` e sobrescrito a cada
deploy. Por isso o banco vai para `/home/data` — senao cada deploy apagaria
os dados da validacao.

### Quando sair do F1

Trocar de plano nao exige recriar nada nem mexer no codigo:

```bash
az appservice plan update --name aerotower-plan --resource-group $GRUPO --sku B1
az webapp config set --name $APP --resource-group $GRUPO --always-on true
```

Quando o Postgres do projeto existir, basta trocar `DATABASE_URL`: o
`app/core/config.py` converte o esquema `postgres://` para `postgresql://`,
que o SQLAlchemy 2.x exige.

O deploy continuo vem do `.github/workflows/azure.yml` — o cabecalho dele
diz qual secret configurar.

## Render

Alternativa gratuita, descrita em `render.yaml`. Dorme depois de ~15 min e o
primeiro pedido seguinte leva ~50s — mesma limitacao do F1, por motivo
parecido.

## Variaveis

| nome | para que | onde |
|---|---|---|
| `MQTT_USER` / `MQTT_PASS` | broker HiveMQ | app settings (nunca no git) |
| `DATABASE_URL` | banco | app settings |
| `MQTT_BROKER` / `MQTT_PORT` | outro broker | opcional |
