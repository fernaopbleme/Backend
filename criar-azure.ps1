# Cria o backend no Azure App Service, plano F1 (gratuito).
#
# Uso:
#   az login                 # com a conta que tem credito
#   .\criar-azure.ps1
#
# E idempotente: rodar de novo nao duplica recurso, so reaplica a config.
# O que ele NAO faz: configurar o secret do GitHub, que e manual (o passo
# fica impresso no fim).

param(
    [string]$Grupo  = "aerotower-rg",
    [string]$App    = "aerotower-backend",
    [string]$Plano  = "aerotower-plan",
    [string]$Regiao = "eastus"
)

$ErrorActionPreference = "Stop"

function Passo($texto) { Write-Host "`n>> $texto" -ForegroundColor Cyan }
function Erro($texto)  { Write-Host "ERRO: $texto" -ForegroundColor Red }

# ── 1. Login ────────────────────────────────────────────────
Passo "Conferindo o login"
$teste = az group list --query "[].name" -o tsv 2>&1 | Out-String
if ($teste -match "AADSTS|invalid_grant|Please run|ERROR") {
    Erro "o token nao vale. Rode 'az logout' e depois 'az login' com a conta que tem credito."
    exit 1
}
$conta = az account show --query "name" -o tsv
$usuario = az account show --query "user.name" -o tsv
Write-Host "   conta: $conta ($usuario)"

# ── 2. Nome do app ──────────────────────────────────────────
# O nome vira <app>.azurewebsites.net, que e unico no mundo inteiro — nao
# so na subscricao. Checar antes evita descobrir no meio da criacao.
Passo "O nome '$App' esta livre?"
$sub = az account show --query "id" -o tsv
$corpo = (@{ name = $App; type = "Microsoft.Web/sites" } | ConvertTo-Json -Compress)
$resposta = az rest --method post `
    --url "https://management.azure.com/subscriptions/$sub/providers/Microsoft.Web/checkNameAvailability?api-version=2023-01-01" `
    --headers "Content-Type=application/json" `
    --body $corpo 2>&1 | Out-String

if ($resposta -match '"nameAvailable":\s*false') {
    $meu = az webapp list --query "[?name=='$App'].name" -o tsv 2>$null
    if ($meu -eq $App) {
        Write-Host "   ja existe nesta subscricao — vou reaproveitar."
    } else {
        Erro "'$App' esta em uso por outra pessoa. Rode de novo com outro nome:"
        Write-Host "        .\criar-azure.ps1 -App aerotower-backend-$(Get-Random -Maximum 9999)"
        exit 1
    }
} else {
    Write-Host "   livre."
}

# ── 3. Recursos ─────────────────────────────────────────────
Passo "Grupo de recursos"
az group create --name $Grupo --location $Regiao --output none
Write-Host "   $Grupo em $Regiao"

Passo "Plano F1 (gratuito, Linux)"
az appservice plan create --name $Plano --resource-group $Grupo `
    --sku F1 --is-linux --output none
Write-Host "   $Plano"

Passo "Web app (Python 3.11)"
az webapp create --name $App --resource-group $Grupo --plan $Plano `
    --runtime "PYTHON:3.11" --output none
Write-Host "   $App"

# ── 4. Configuracao ─────────────────────────────────────────
# --always-on NAO entra: o F1 nao suporta e a chamada falha.
# --web-sockets-enabled e obrigatorio, senao o /ws/sensores nao conecta e
# o erro no navegador parece problema de CORS.
Passo "Comando de inicializacao e WebSocket"
az webapp config set --name $App --resource-group $Grupo `
    --startup-file "startup.sh" --web-sockets-enabled true --output none
Write-Host "   startup.sh, websockets ligados"

# ── 5. Variaveis de ambiente ────────────────────────────────
# As credenciais saem do .env local, para nao serem redigitadas (e para
# nao passarem pelo historico do PowerShell).
Passo "Variaveis de ambiente"
$mqttUser = ""
$mqttPass = ""
if (Test-Path ".env") {
    foreach ($linha in Get-Content ".env") {
        if ($linha -match '^\s*MQTT_USER\s*=\s*(.+)$') { $mqttUser = $Matches[1].Trim() }
        if ($linha -match '^\s*MQTT_PASS\s*=\s*(.+)$') { $mqttPass = $Matches[1].Trim() }
    }
}
if ([string]::IsNullOrWhiteSpace($mqttUser) -or [string]::IsNullOrWhiteSpace($mqttPass)) {
    Erro "nao achei MQTT_USER/MQTT_PASS no .env. Preencha (modelo em .env.example) e rode de novo."
    exit 1
}

# O banco vai para /home/data porque /home persiste entre reinicios e
# /home/site/wwwroot e sobrescrito a cada deploy — la, cada publicacao
# apagaria os dados.
az webapp config appsettings set --name $App --resource-group $Grupo --settings `
    "SCM_DO_BUILD_DURING_DEPLOYMENT=true" `
    "MQTT_USER=$mqttUser" `
    "MQTT_PASS=$mqttPass" `
    "DATABASE_URL=sqlite:////home/data/plantas.db" --output none
Write-Host "   4 variaveis definidas (MQTT_PASS lida do .env, nao impressa)"

# ── 6. Resultado ────────────────────────────────────────────
$host_ = az webapp show --name $App --resource-group $Grupo --query "defaultHostName" -o tsv
Write-Host "`n================================================" -ForegroundColor Green
Write-Host " Backend criado: https://$host_" -ForegroundColor Green
Write-Host "================================================`n" -ForegroundColor Green

Write-Host "Falta publicar o codigo. Dois passos manuais:"
Write-Host ""
Write-Host "1. Baixar o perfil de publicacao:"
Write-Host "   az webapp deployment list-publishing-profiles --name $App --resource-group $Grupo --xml > perfil.xml"
Write-Host ""
Write-Host "2. Em github.com/fernaopbleme/Backend > Settings > Secrets and"
Write-Host "   variables > Actions > New repository secret:"
Write-Host "     nome:     AZURE_WEBAPP_PUBLISH_PROFILE"
Write-Host "     conteudo: o perfil.xml inteiro"
Write-Host ""
if ($App -ne "aerotower-backend") {
    Write-Host "3. ATENCAO: o nome mudou. Troque AZURE_WEBAPP_NAME em" -ForegroundColor Yellow
    Write-Host "   .github/workflows/azure.yml para '$App'." -ForegroundColor Yellow
    Write-Host ""
}
Write-Host "Depois disso, todo push na branch apresentacao publica sozinho."
Write-Host "No F1 a aplicacao dorme: antes de apresentar, abra a URL acima e"
Write-Host "espere responder ANTES de ligar o simulador."
