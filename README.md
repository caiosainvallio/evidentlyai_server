# EvidentlyAI Server

Servidor EvidentlyAI para monitoramento de modelos ML com Docker Compose. Esta implementação fornece uma solução completa para deploy do EvidentlyAI com MinIO como storage backend, ideal para ambientes de produção e desenvolvimento.

## 📋 Índice

- [Início Rápido](#-início-rápido)
- [Pré-requisitos](#-pré-requisitos)
- [Instalação](#-instalação)
- [Configuração](#️-configuração)
- [Uso](#-uso)
- [Serviços](#-serviços)
- [Comandos Disponíveis](#-comandos-disponíveis)
- [Integração](#-integração)
- [Troubleshooting](#-troubleshooting)
- [Produção](#-produção)
- [Contribuição](#-contribuição)

## 🚀 Início Rápido

```bash
# 1. Clone o repositório
git clone <repository-url>
cd evidentlyai_server

# 2. Configurar variáveis de ambiente (opcional)
cp env.example .env

# 3. Iniciar serviços
make run

# 4. Verificar se está funcionando
make status

# 5. Acessar dashboard
open http://localhost:8000
```

## 📋 Pré-requisitos

### Software Necessário
- **Docker**: versão 20.10+
- **Docker Compose**: versão 2.0+
- **Make**: para comandos simplificados (opcional)

### Verificar Instalação
```bash
# Verificar Docker
docker --version
docker-compose --version

# Verificar portas disponíveis
netstat -an | grep -E ':(8000|9000|9001)'
```

### Recursos de Sistema
- **RAM**: mínimo 2GB, recomendado 4GB+
- **Disk**: mínimo 5GB livres
- **CPU**: 2+ cores recomendados

## 📦 Instalação

### Método 1: Clone do Repositório
```bash
git clone <repository-url>
cd evidentlyai_server
```

### Método 2: Download Manual
```bash
# Baixar apenas os arquivos essenciais
wget <repository-url>/docker-compose.yaml
wget <repository-url>/Makefile
wget <repository-url>/env.example
```

### Verificação da Instalação
```bash
# Verificar arquivos necessários
ls -la docker-compose.yaml Makefile env.example

# Testar sintaxe do docker-compose
docker-compose config
```

## ⚙️ Configuração

### Variáveis de Ambiente

Copie e edite o arquivo de configuração:
```bash
cp env.example .env
nano .env  # ou vim, code, etc.
```

#### Configurações Principais

| Variável | Padrão | Descrição |
|----------|--------|-----------|
| `EVIDENTLY_SERVER_HOST` | `localhost` | Host do servidor EvidentlyAI |
| `EVIDENTLY_SERVER_PORT` | `8000` | Porta do servidor EvidentlyAI |
| `EVIDENTLY_WORKSPACE_PATH` | `./workspace` | Caminho do workspace local |
| `MINIO_ROOT_USER` | `minioadmin` | Usuário admin do MinIO |
| `MINIO_ROOT_PASSWORD` | `minioadmin123` | Senha admin do MinIO |
| `MINIO_DEFAULT_BUCKET` | `evidently-workspace` | Bucket padrão |

#### Configurações de Produção
```bash
# Para ambientes de produção, altere:
EVIDENTLY_SERVER_HOST=0.0.0.0
MINIO_ROOT_PASSWORD=senha-super-secreta
DEBUG_MODE=false
LOG_LEVEL=WARNING
```

### Configuração de Rede

#### Portas Utilizadas
- **8000**: EvidentlyAI Dashboard
- **9000**: MinIO API
- **9001**: MinIO Console

#### Customizar Portas
Para alterar as portas, edite o `docker-compose.yaml`:
```yaml
services:
  evidently-service:
    ports:
      - "8080:8000"  # Alterar porta externa
```

### Volumes e Persistência

#### Volumes Configurados
- `./workspace`: Dados do workspace EvidentlyAI (bind mount)
- `minio_data`: Dados do MinIO (volume Docker)
- `evidently_data`: Cache e dados temporários (volume Docker)

#### Backup dos Dados
```bash
# Backup do workspace
tar -czf backup-workspace-$(date +%Y%m%d).tar.gz ./workspace

# Backup dos volumes Docker
docker run --rm -v evidentlyai_server_minio_data:/data -v $(pwd):/backup busybox tar czf /backup/minio-backup-$(date +%Y%m%d).tar.gz /data
```

## 🔧 Uso

### Inicialização dos Serviços

#### Primeira Execução
```bash
# Build das imagens (se necessário)
make build

# Iniciar em background
make run

# Aguardar inicialização (30-60s)
sleep 30

# Verificar saúde dos serviços
make status
```

#### Verificação de Saúde
```bash
# Status dos containers
make status

# Logs em tempo real
make logs

# Logs específicos
make logs-evidently
make logs-minio

# Teste de conectividade
curl -f http://localhost:8000/health || echo "EvidentlyAI não disponível"
curl -f http://localhost:9000/minio/health/live || echo "MinIO não disponível"
```

### Acesso aos Serviços

#### EvidentlyAI Dashboard
- **URL**: http://localhost:8000
- **Funcionalidades**:
  - Visualização de projetos
  - Reports e métricas
  - Configuração de dashboards
  - API REST

#### MinIO Console
- **URL**: http://localhost:9001
- **Credenciais**: `minioadmin` / `minioadmin123`
- **Funcionalidades**:
  - Gerenciar buckets
  - Upload/download de arquivos
  - Configurações de acesso
  - Monitoramento

### Parada dos Serviços

```bash
# Parada normal
make stop

# Parada forçada (se necessário)
docker-compose kill

# Limpeza completa (remove tudo)
make clear_all
```

## 🐳 Serviços

### EvidentlyAI Service

#### Especificações
- **Imagem**: `evidently/evidently-service:latest`
- **Porta**: 8000 (HTTP)
- **Workspace**: `/app/workspace`
- **Dependências**: MinIO

#### Configurações
```yaml
environment:
  - EVIDENTLY_WORKSPACE_PATH=/app/workspace
volumes:
  - ./workspace:/app/workspace
  - evidently_data:/app/data
```

#### API Endpoints
- `GET /` - Dashboard principal
- `GET /api/projects` - Lista projetos
- `GET /docs` - Documentação Swagger
- `GET /health` - Health check

### MinIO Storage

#### Especificações
- **Imagem**: `minio/minio:latest`
- **API**: Porta 9000
- **Console**: Porta 9001
- **Storage**: `/data`

#### Configurações
```yaml
environment:
  - MINIO_ROOT_USER=minioadmin
  - MINIO_ROOT_PASSWORD=minioadmin123
command: server /data --console-address ":9001"
```

#### Health Check
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:9000/minio/health/live"]
  interval: 30s
  timeout: 20s
  retries: 3
```

### MinIO Init Service

#### Funcionalidade
- Cria bucket padrão automaticamente
- Configura políticas de acesso
- Executa uma única vez na inicialização

#### Script de Inicialização
```bash
until mc alias set myminio http://minio:9000 minioadmin minioadmin123; do
  echo 'Aguardando MinIO...';
  sleep 2;
done;
mc mb myminio/evidently-workspace --ignore-existing;
mc policy set public myminio/evidently-workspace;
```

## 🛠️ Comandos Disponíveis

### Comandos Básicos

| Comando | Descrição | Exemplo |
|---------|-----------|---------|
| `make build` | Construir imagens Docker | `make build` |
| `make run` | Iniciar containers em background | `make run` |
| `make stop` | Parar containers | `make stop` |
| `make restart` | Reiniciar todos os serviços | `make restart` |
| `make status` | Mostrar status dos containers | `make status` |

### Comandos de Monitoramento

| Comando | Descrição | Exemplo |
|---------|-----------|---------|
| `make logs` | Logs de todos os serviços | `make logs` |
| `make logs-evidently` | Logs apenas do EvidentlyAI | `make logs-evidently` |
| `make logs-minio` | Logs apenas do MinIO | `make logs-minio` |

### Comandos de Limpeza

| Comando | Descrição | Cuidado |
|---------|-----------|---------|
| `make clear_all` | Remove containers, volumes e imagens | ⚠️ Remove TODOS os dados |

### Comandos Docker Diretos

```bash
# Execução direta (sem Makefile)
docker-compose up -d
docker-compose down
docker-compose ps
docker-compose logs -f

# Comandos avançados
docker-compose exec evidently-service bash
docker-compose exec minio bash
```

## 🔗 Integração

### Integração Python

#### Instalação do Cliente
```bash
pip install evidently[server]
```

#### Exemplo Básico
```python
from evidently.ui.workspace import RemoteWorkspace
from evidently import Report
from evidently.presets import DataDriftPreset

# Conectar ao workspace remoto
workspace = RemoteWorkspace("http://localhost:8000")

# Listar projetos existentes
projects = workspace.list_projects()
print(f"Projetos encontrados: {len(projects)}")

# Criar novo projeto
project = workspace.create_project(
    name="ml-monitoring",
    description="Monitoramento de modelo ML"
)

# Criar e enviar relatório
report = Report(metrics=[DataDriftPreset()])
report.run(reference_data=ref_data, current_data=current_data)

# Adicionar ao workspace
workspace.add_report(project.id, report)
```

#### Script de Monitoramento Contínuo
```python
import schedule
import time
from evidently.ui.workspace import RemoteWorkspace
from evidently import Report
from evidently.presets import DataDriftPreset

def monitor_data_drift():
    workspace = RemoteWorkspace("http://localhost:8000")
    # Sua lógica de monitoramento aqui
    pass

# Executar a cada hora
schedule.every().hour.do(monitor_data_drift)

while True:
    schedule.run_pending()
    time.sleep(60)
```

### Integração com CI/CD

#### GitHub Actions
```yaml
name: ML Monitoring
on:
  schedule:
    - cron: '0 */6 * * *'  # A cada 6 horas

jobs:
  monitor:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.8'
      - name: Install dependencies
        run: pip install evidently[server] pandas
      - name: Run monitoring
        run: python scripts/monitor.py
        env:
          EVIDENTLY_URL: ${{ secrets.EVIDENTLY_URL }}
```

### Integração com MLOps

#### MLflow Integration
```python
import mlflow
from evidently.ui.workspace import RemoteWorkspace

# Ao final do treinamento MLflow
with mlflow.start_run():
    # ... seu código de treinamento ...
    
    # Enviar métricas para EvidentlyAI
    workspace = RemoteWorkspace("http://localhost:8000")
    # ... código de monitoramento ...
```

## 🔍 Troubleshooting

### Problemas Comuns

#### Portas em Uso
```bash
# Verificar processos usando as portas
lsof -i :8000
lsof -i :9000
lsof -i :9001

# Parar processos conflitantes
sudo kill -9 $(lsof -t -i:8000)
```

#### Problemas de Permissão
```bash
# Corrigir permissões do workspace
sudo chown -R $USER:$USER ./workspace
chmod -R 755 ./workspace
```

#### Containers Não Iniciam
```bash
# Verificar logs de erro
docker-compose logs evidently-service
docker-compose logs minio

# Verificar recursos do sistema
docker system df
docker system events &
```

#### MinIO Não Conecta
```bash
# Resetar configuração MinIO
docker-compose down
docker volume rm evidentlyai_server_minio_data
docker-compose up -d
```

### Debugging Avançado

#### Logs Detalhados
```bash
# Habilitar logs verbosos
export COMPOSE_LOG_LEVEL=DEBUG
docker-compose up

# Logs do Docker daemon
sudo journalctl -u docker.service
```

#### Acesso aos Containers
```bash
# Shell no container EvidentlyAI
docker-compose exec evidently-service bash

# Shell no container MinIO
docker-compose exec minio bash

# Verificar conectividade entre containers
docker-compose exec evidently-service ping minio
```

#### Monitoramento de Recursos
```bash
# Uso de recursos dos containers
docker stats

# Espaço em disco dos volumes
docker system df -v
```

### Soluções por Erro

#### "Connection refused" no EvidentlyAI
1. Verificar se o container está rodando: `docker-compose ps`
2. Verificar logs: `make logs-evidently`
3. Aguardar inicialização completa (até 60s)
4. Verificar configurações de rede: `docker-compose config`

#### MinIO Console inacessível
1. Verificar porta 9001: `netstat -an | grep 9001`
2. Tentar acessar via IP: `http://127.0.0.1:9001`
3. Verificar logs: `make logs-minio`
4. Resetar senha: Ver seção de configuração

#### Workspace vazio após restart
1. Verificar bind mount: `ls -la ./workspace`
2. Verificar permissões: `ls -la`
3. Verificar volumes: `docker volume ls`
4. Restaurar backup se necessário

## 🚀 Produção

### Configurações de Produção

#### docker-compose.prod.yaml
```yaml
version: '3.8'
services:
  evidently-service:
    image: evidently/evidently-service:latest
    restart: always
    environment:
      - EVIDENTLY_WORKSPACE_PATH=/app/workspace
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '1.0'
        reservations:
          memory: 1G
          cpus: '0.5'
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s

  minio:
    image: minio/minio:latest
    restart: always
    environment:
      - MINIO_ROOT_USER=${MINIO_ROOT_USER}
      - MINIO_ROOT_PASSWORD=${MINIO_ROOT_PASSWORD}
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '0.5'
```

#### Variáveis de Produção
```bash
# .env.production
EVIDENTLY_SERVER_HOST=0.0.0.0
MINIO_ROOT_USER=admin
MINIO_ROOT_PASSWORD=senha-super-secreta-123
DEBUG_MODE=false
LOG_LEVEL=WARNING
REQUEST_TIMEOUT=60
```

### Proxy Reverso

#### Nginx Configuration
```nginx
upstream evidently {
    server localhost:8000;
}

server {
    listen 80;
    server_name evidently.mycompany.com;
    
    location / {
        proxy_pass http://evidently;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Monitoramento

#### Health Checks
```bash
#!/bin/bash
# health-check.sh
curl -f http://localhost:8000/health || exit 1
curl -f http://localhost:9000/minio/health/live || exit 1
echo "All services healthy"
```

#### Alertas Básicos
```bash
#!/bin/bash
# alerts.sh
if ! curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "EvidentlyAI DOWN" | mail -s "Alert: EvidentlyAI" admin@company.com
fi
```

### Backup Automatizado

#### Script de Backup
```bash
#!/bin/bash
# backup.sh
BACKUP_DIR="/backups/evidently"
DATE=$(date +%Y%m%d_%H%M%S)

# Backup workspace
tar -czf "$BACKUP_DIR/workspace_$DATE.tar.gz" ./workspace

# Backup MinIO
docker run --rm \
  -v evidentlyai_server_minio_data:/data \
  -v "$BACKUP_DIR":/backup \
  busybox tar czf "/backup/minio_$DATE.tar.gz" /data

# Limpar backups antigos (> 30 dias)
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +30 -delete
```

#### Cron para Backup Diário
```bash
# crontab -e
0 2 * * * /path/to/backup.sh
```

### Segurança

#### Configurações de Segurança
```yaml
# Adicionar ao docker-compose.yaml
services:
  evidently-service:
    security_opt:
      - no-new-privileges:true
    read_only: false
    tmpfs:
      - /tmp:noexec,nosuid,size=100m
```

#### Firewall Rules
```bash
# Permitir apenas portas necessárias
sudo ufw allow 8000/tcp  # EvidentlyAI
sudo ufw allow 9001/tcp  # MinIO Console (apenas admin)
sudo ufw deny 9000/tcp   # MinIO API (apenas interno)
```

## 🤝 Contribuição

### Desenvolvimento Local

```bash
# Fork e clone
git clone https://github.com/your-user/evidentlyai_server.git
cd evidentlyai_server

# Criar branch para feature
git checkout -b feature/nova-funcionalidade

# Fazer alterações e testar
make run
# ... fazer testes ...

# Commit e push
git add .
git commit -m "feat: nova funcionalidade"
git push origin feature/nova-funcionalidade
```

### Reportar Issues

Ao reportar problemas, inclua:
- Versão do Docker e Docker Compose
- Sistema operacional
- Logs relevantes (`make logs`)
- Passos para reproduzir
- Configurações (.env mascarado)

### Sugestões de Melhorias

- Configurações adicionais
- Novos comandos no Makefile
- Documentação melhorada
- Scripts de automação
- Integrações com outras ferramentas

---

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.

## 🔗 Links Úteis

- [EvidentlyAI Documentation](https://docs.evidentlyai.com/)
- [MinIO Documentation](https://docs.min.io/)
- [Docker Compose Reference](https://docs.docker.com/compose/)
- [EvidentlyAI GitHub](https://github.com/evidentlyai/evidently)

---

**⚡ Tip**: Para uma experiência otimizada, considere usar um SSD e pelo menos 4GB de RAM em produção.
