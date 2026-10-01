#!/usr/bin/env bash
#
# Comando de inicializacao do App Service.
# No portal: Configuration > General settings > Startup Command -> startup.sh
#
# Por que nao o padrao da Azure (gunicorn com -w 4): este backend NAO pode
# rodar em mais de um processo.
#
#   * O subscriber MQTT sobe no lifespan da aplicacao. Com 4 workers seriam
#     4 conexoes no broker, e cada leitura do sensor entraria 4 vezes no
#     banco.
#   * O /ws/sensores transmite a leitura para os clientes conectados AQUELE
#     processo. Um cliente atendido pelo worker 1 nunca veria o dado que
#     chegou no worker 2 — o dashboard ficaria parado sem erro nenhum.
#
# Um processo resolve os dois. Para escalar de verdade seria preciso tirar o
# MQTT da aplicacao web e por o WebSocket atras de um broker compartilhado;
# nao e o caso agora.
#
# O App Service define $PORT; 8000 e o default da imagem Python.
exec python -m uvicorn main:app --host 0.0.0.0 --port "${PORT:-8000}"
