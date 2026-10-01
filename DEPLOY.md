# Deploy do backend

Duas opcoes, na ordem em que foram consideradas. O codigo serve as duas sem
mudanca: tudo que varia esta em variavel de ambiente.

## Azure App Service

Precisa de uma subscricao com credito. O plano **F1 (gratis) nao serve**:
ele nao tem Always On, e sem Always On o App Service descarrega a aplicacao
depois de ~20 min sem acesso — o que mata a conexao MQTT e para de gravar
leitura de sensor sem erro nenhum aparecer. Use B1 ou acima.

```bash
GRUPO=aerotower-rg
APP=aerotower-backend          # tem de ser unico no .azurewebsites.net
REGIAO=eastus

az group create --name $GRUPO --location $REGIAO

az appservice plan create --name aerotower-plan --resource-group $GRUPO \
  --sku B1 --is-linux

az webapp create --name $APP --resource-group $GRUPO \
  --plan aerotower-plan --runtime "PYTHON:3.11"

# Um processo so: ver o cabecalho de startup.sh para o porque.
az webapp config set --name $APP --resource-group $GRUPO \
  --startup-file startup.sh \
  --web-sockets-enabled true \
  --always-on true

# O /ws/sensores nao conecta sem web-sockets-enabled, e falha de um jeito
# que parece problema de CORS no navegador.

az webapp config appsettings set --name $APP --resource-group $GRUPO \
  --settings \
    SCM_DO_BUILD_DURING_DEPLOYMENT=true \
    MQTT_USER="<usuario do hivemq>" \
    MQTT_PASS="<senha nova do hivemq>" \
    DATABASE_URL="sqlite:////home/data/plantas.db"
```

`/home` persiste entre reinicios do App Service; `/home/site/wwwroot` e
sobrescrito a cada deploy. Por isso o banco vai para `/home/data` e nao
para a pasta da aplicacao — senao cada deploy apagaria os dados.

Quando o banco Postgres do projeto existir, e so trocar `DATABASE_URL`:
o `app/core/config.py` converte o esquema `postgres://` para
`postgresql://`, que o SQLAlchemy 2.x exige.

O deploy continuo vem do `.github/workflows/azure.yml` — veja o cabecalho
dele para o secret que falta configurar.

## Render

Alternativa gratuita, descrita em `render.yaml`. O servico dorme depois de
~15 min sem acesso e o primeiro pedido seguinte leva ~50s; enquanto dorme,
o MQTT fica desconectado. Serve para manter o backend de pe sem credito,
nao para coletar dados continuamente.

## Variaveis

| nome | para que | onde |
|---|---|---|
| `MQTT_USER` / `MQTT_PASS` | broker HiveMQ | app settings (nunca no git) |
| `DATABASE_URL` | banco | app settings |
| `MQTT_BROKER` / `MQTT_PORT` | outro broker | opcional |

Localmente, `.env` na raiz cobre as duas primeiras. Modelo em `.env.example`.
