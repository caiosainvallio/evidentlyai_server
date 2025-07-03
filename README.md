# 📊 EvidentlyAI Server

**Servidor EvidentlyAI para monitoramento e avaliação de modelos ML com interface visual completa.**

[![Python](https://img.shields.io/badge/Python-3.13+-blue.svg)](https://python.org)
[![EvidentlyAI](https://img.shields.io/badge/EvidentlyAI-0.7.9+-green.svg)](https://evidentlyai.com)
[![Docker](https://img.shields.io/badge/Docker-✓-blue.svg)](https://docker.com)
[![MinIO](https://img.shields.io/badge/MinIO-✓-red.svg)](https://min.io)

## 📋 Índice

- [Sobre o Projeto](#sobre-o-projeto)
- [Funcionalidades](#funcionalidades)
- [Pré-requisitos](#pré-requisitos)
- [Instalação e Configuração](#instalação-e-configuração)
- [Uso Básico](#uso-básico)
- [Guia de Experimentos](#guia-de-experimentos)
- [Exemplos Práticos](#exemplos-práticos)
- [API e Integração](#api-e-integração)
- [Monitoramento em Produção](#monitoramento-em-produção)
- [Troubleshooting](#troubleshooting)
- [Contribuição](#contribuição)

## 🎯 Sobre o Projeto

Este projeto fornece uma configuração completa do **EvidentlyAI** com Docker, incluindo:

- **Evidently Service**: Servidor principal para avaliação e monitoramento de ML
- **MinIO**: Storage de objetos para armazenamento de dados e relatórios
- **Interface Web**: Dashboard interativo para visualização de métricas
- **Scripts Python**: Exemplos práticos de integração via API

### O que é o EvidentlyAI?

O [EvidentlyAI](https://evidentlyai.com) é uma framework open-source para:

- ✅ **Avaliação de Modelos**: 100+ métricas para ML
- 📊 **Monitoramento**: Detecção de drift de dados e performance
- 🧪 **Testes**: Test suites com condições pass/fail
- 📈 **Reports**: Relatórios visuais interativos

## 🚀 Funcionalidades

### 📈 Monitoramento de Modelos ML
- **Data Drift**: Detecção de mudanças na distribuição dos dados
- **Model Performance**: Métricas de classificação, regressão, ranking
- **Data Quality**: Validação de qualidade dos dados
- **Feature Monitoring**: Monitoramento de features específicas

### 🔧 Funcionalidades Técnicas
- **Dashboard Web**: Interface visual rica e interativa
- **API REST**: Integração programática completa
- **Storage Persistente**: Armazenamento com MinIO
- **Docker Setup**: Configuração containerizada
- **Export de Dados**: JSON, HTML, Python dict

## 📋 Pré-requisitos

- **Docker** 20.10+ e **Docker Compose** 2.0+
- **Python** 3.13+
- **Git**
- **Make** (opcional, para comandos simplificados)

### Verificação dos Pré-requisitos

```bash
# Verificar versões
docker --version
docker-compose --version
python --version
git --version
```

## 🛠 Instalação e Configuração

### 1. Clone do Repositório

```bash
git clone <your-repo-url>
cd evidentlyai_server
```

### 2. Configuração do Ambiente

```bash
# Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Instalar dependências
pip install -e .
```

### 3. Inicialização dos Serviços

```bash
# Construir e iniciar todos os serviços
make run

# Ou usando docker-compose diretamente
docker-compose up -d
```

### 4. Verificação da Instalação

```bash
# Verificar status dos serviços
make status

# Acompanhar logs
make logs
```

## 🎮 Uso Básico

### Acessando os Serviços

Após inicializar, os seguintes serviços estarão disponíveis:

- **EvidentlyAI UI**: http://localhost:8000
- **MinIO Console**: http://localhost:9001
  - Usuário: `minioadmin`
  - Senha: `minioadmin123`

### Primeiro Experimento

```bash
# Executar exemplo demo
make demo

# Ou diretamente
python examples/remote_demo_project.py
```

## 📚 Guia de Experimentos

### Experimento 1: Avaliação de Data Drift

```python
import pandas as pd
from evidently import Report
from evidently.presets import DataDriftPreset
from examples.evidently_client import EvidentlyClient

# 1. Preparar dados
reference_data = pd.read_csv('data/reference.csv')
current_data = pd.read_csv('data/current.csv')

# 2. Criar cliente
client = EvidentlyClient(base_url='http://localhost:8000')

# 3. Criar projeto
project = client.create_project("Data Drift Analysis", "Análise de drift em dados de produção")

# 4. Executar avaliação
report = Report(presets=[DataDriftPreset()])
report.run(reference_data=reference_data, current_data=current_data)

# 5. Enviar para servidor
client.send_report(project.id, report)
```

### Experimento 2: Monitoramento de Performance de Modelo ML

```python
from evidently.presets import ClassificationPreset
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

# 1. Preparar dados e modelo
iris = load_iris(as_frame=True)
X_train, X_test, y_train, y_test = train_test_split(
    iris.data, iris.target, test_size=0.3, random_state=42
)

model = RandomForestClassifier(random_state=42)
model.fit(X_train, y_train)
predictions = model.predict(X_test)

# 2. Preparar dados para avaliação
test_data = X_test.copy()
test_data['target'] = y_test
test_data['prediction'] = predictions

# 3. Criar relatório de classificação
report = Report(presets=[ClassificationPreset()])
report.run(reference_data=None, current_data=test_data)

# 4. Enviar para servidor
client.send_report(project.id, report)
```

## 🔧 Exemplos Práticos

### Script de Monitoramento Contínuo

```python
import time
import schedule
from examples.evidently_client import EvidentlyClient
from examples.data_generator import generate_synthetic_data

def daily_monitoring():
    """Executa monitoramento diário automaticamente"""
    client = EvidentlyClient()
    
    # Gerar dados sintéticos (substitua pela sua fonte de dados)
    current_data = generate_synthetic_data()
    
    # Executar avaliações
    drift_report = client.run_data_drift_analysis(current_data)
    quality_report = client.run_data_quality_check(current_data)
    
    print(f"Relatórios enviados: {drift_report.id}, {quality_report.id}")

# Agendar execução diária
schedule.every().day.at("09:00").do(daily_monitoring)

while True:
    schedule.run_pending()
    time.sleep(60)
```

### Integração com Pipeline ML

```python
def model_validation_pipeline(model, X_test, y_test, X_reference, y_reference):
    """Pipeline de validação de modelo integrado com Evidently"""
    
    # 1. Fazer predições
    predictions = model.predict(X_test)
    probabilities = model.predict_proba(X_test)
    
    # 2. Preparar dados
    test_data = X_test.copy()
    test_data['target'] = y_test
    test_data['prediction'] = predictions
    
    reference_data = X_reference.copy()
    reference_data['target'] = y_reference
    
    # 3. Executar avaliações
    client = EvidentlyClient()
    
    # Data Drift
    drift_report = Report(presets=[DataDriftPreset()])
    drift_report.run(reference_data, test_data)
    
    # Model Performance
    perf_report = Report(presets=[ClassificationPreset()])
    perf_report.run(reference_data, test_data)
    
    # 4. Verificar resultados
    drift_results = drift_report.as_dict()
    perf_results = perf_report.as_dict()
    
    # 5. Tomar decisões baseadas nos resultados
    if drift_results['metrics'][0]['result']['drift_detected']:
        print("⚠️  Data drift detectado! Considere retreinar o modelo.")
        return False
    
    accuracy = perf_results['metrics'][0]['result']['current']['accuracy']
    if accuracy < 0.85:
        print(f"⚠️  Accuracy baixa: {accuracy:.3f}. Modelo precisa ser melhorado.")
        return False
    
    print("✅ Modelo validado com sucesso!")
    return True
```

## 🌐 API e Integração

### Cliente Python Personalizado

```python
class EvidentlyClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def create_project(self, name, description=""):
        """Criar novo projeto"""
        response = self.session.post(
            f"{self.base_url}/api/projects",
            json={"name": name, "description": description}
        )
        return response.json()
    
    def upload_data(self, project_id, data, data_type="reference"):
        """Upload de dados para projeto"""
        files = {'file': ('data.csv', data.to_csv(), 'text/csv')}
        response = self.session.post(
            f"{self.base_url}/api/projects/{project_id}/data/{data_type}",
            files=files
        )
        return response.json()
    
    def run_report(self, project_id, preset_name, config=None):
        """Executar relatório"""
        payload = {
            "preset": preset_name,
            "config": config or {}
        }
        response = self.session.post(
            f"{self.base_url}/api/projects/{project_id}/reports",
            json=payload
        )
        return response.json()
    
    def get_report(self, project_id, report_id):
        """Obter relatório específico"""
        response = self.session.get(
            f"{self.base_url}/api/projects/{project_id}/reports/{report_id}"
        )
        return response.json()
```

### Integração via cURL

```bash
# Criar projeto
curl -X POST http://localhost:8000/api/projects \
  -H "Content-Type: application/json" \
  -d '{"name": "My Project", "description": "Test project"}'

# Upload de dados
curl -X POST http://localhost:8000/api/projects/{project_id}/data/reference \
  -F "file=@reference_data.csv"

# Executar relatório
curl -X POST http://localhost:8000/api/projects/{project_id}/reports \
  -H "Content-Type: application/json" \
  -d '{"preset": "DataDriftPreset", "config": {}}'
```

## 📊 Monitoramento em Produção

### Configuração de Alertas

```python
class AlertManager:
    def __init__(self, client):
        self.client = client
        self.thresholds = {
            'data_drift': 0.1,
            'accuracy_drop': 0.05,
            'missing_values': 0.02
        }
    
    def check_alerts(self, report_results):
        """Verificar se alertas devem ser disparados"""
        alerts = []
        
        # Verificar data drift
        if report_results.get('drift_score', 0) > self.thresholds['data_drift']:
            alerts.append({
                'type': 'data_drift',
                'severity': 'high',
                'message': 'Data drift detectado acima do threshold'
            })
        
        # Verificar queda de performance
        current_accuracy = report_results.get('accuracy', 1.0)
        baseline_accuracy = report_results.get('baseline_accuracy', 1.0)
        
        if (baseline_accuracy - current_accuracy) > self.thresholds['accuracy_drop']:
            alerts.append({
                'type': 'performance_drop',
                'severity': 'medium',
                'message': f'Accuracy caiu de {baseline_accuracy:.3f} para {current_accuracy:.3f}'
            })
        
        return alerts
    
    def send_alerts(self, alerts):
        """Enviar alertas (implementar integração com Slack, email, etc.)"""
        for alert in alerts:
            print(f"🚨 ALERT [{alert['severity']}]: {alert['message']}")
            # Implementar envio real aqui
```

### Dashboard Customizado

```python
import streamlit as st
import plotly.express as px

def create_monitoring_dashboard():
    """Criar dashboard customizado com Streamlit"""
    
    st.title("🔍 ML Model Monitoring Dashboard")
    
    # Sidebar para seleção
    st.sidebar.header("Configurações")
    project_id = st.sidebar.selectbox("Projeto", get_project_list())
    time_range = st.sidebar.selectbox("Período", ["7d", "30d", "90d"])
    
    # Métricas principais
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Accuracy", "94.2%", "+1.2%")
    with col2:
        st.metric("Data Drift", "0.05", "-0.02")
    with col3:
        st.metric("Missing Values", "0.1%", "0.0%")
    with col4:
        st.metric("Predictions/day", "1,234", "+56")
    
    # Gráficos
    st.subheader("📈 Performance ao Longo do Tempo")
    
    # Exemplo de dados (substitua por dados reais)
    performance_data = get_performance_data(project_id, time_range)
    fig = px.line(performance_data, x='date', y='accuracy', title='Model Accuracy')
    st.plotly_chart(fig, use_container_width=True)
    
    # Data drift heatmap
    st.subheader("🔥 Heatmap de Data Drift")
    drift_data = get_drift_data(project_id, time_range)
    fig_heatmap = px.imshow(drift_data, title='Feature Drift Over Time')
    st.plotly_chart(fig_heatmap, use_container_width=True)

if __name__ == "__main__":
    create_monitoring_dashboard()
```

## 🐛 Troubleshooting

### Problemas Comuns

#### 1. Erro de Conexão com MinIO
```bash
# Verificar se MinIO está rodando
docker-compose ps minio

# Restart do MinIO
docker-compose restart minio

# Verificar logs
make logs-minio
```

#### 2. Evidently Service não Responde
```bash
# Verificar logs do serviço
make logs-evidently

# Restart do serviço
docker-compose restart evidently-service

# Verificar se o workspace está montado corretamente
ls -la ./workspace/
```

#### 3. Erro de Permissões no Workspace
```bash
# Corrigir permissões (Linux/Mac)
sudo chown -R $USER:$USER ./workspace/
chmod -R 755 ./workspace/
```

#### 4. Porta já em Uso
```bash
# Verificar processos usando as portas
lsof -i :8000  # Evidently
lsof -i :9000  # MinIO API
lsof -i :9001  # MinIO Console

# Parar serviços em conflito ou alterar portas no docker-compose.yaml
```

### Comandos de Diagnóstico

```bash
# Status completo dos serviços
make status

# Logs de todos os serviços
make logs

# Logs específicos
make logs-evidently
make logs-minio

# Limpeza completa (cuidado: remove todos os dados)
make clear_all

# Reconstruir serviços
make build
```

### Configuração de Debug

```python
import logging

# Configurar logging detalhado
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Para debug do cliente
import requests
import http.client as http_client

http_client.HTTPConnection.debuglevel = 1
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True
```

## 🤝 Contribuição

### Como Contribuir

1. **Fork** do repositório
2. Crie uma **branch** para sua feature (`git checkout -b feature/nova-funcionalidade`)
3. **Commit** suas mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
4. **Push** para a branch (`git push origin feature/nova-funcionalidade`)
5. Crie um **Pull Request**

### Padrões de Código

```bash
# Formatting com black
black .

# Linting com ruff
ruff check .

# Type checking com mypy
mypy src/
```

### Testes

```bash
# Executar todos os testes
pytest

# Testes com coverage
pytest --cov=src/

# Testes específicos
pytest tests/test_client.py::test_create_project
```

## 📝 Licença

Este projeto está licenciado sob a [MIT License](LICENSE).

## 🔗 Links Úteis

- **Documentação Oficial**: https://docs.evidentlyai.com/
- **GitHub EvidentlyAI**: https://github.com/evidentlyai/evidently
- **Community Discord**: https://discord.gg/xZjKRaNp8b
- **Evidently Cloud**: https://www.evidentlyai.com/
- **Exemplos e Tutoriais**: https://github.com/evidentlyai/evidently/tree/main/examples

## 📞 Suporte

- **Issues**: Reporte bugs e solicite features via [GitHub Issues](https://github.com/seu-repo/issues)
- **Discussões**: Participe das discussões da comunidade
- **Email**: contato@seudominio.com

---

**⭐ Se este projeto foi útil, considere dar uma estrela no GitHub!**
