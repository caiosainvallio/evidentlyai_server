# 🚀 Guia de Uso Rápido - EvidentlyAI Server

Este guia te ajudará a começar a usar o EvidentlyAI Server em poucos minutos.

## 📋 Pré-requisitos Rápidos

Antes de começar, certifique-se de ter:

```bash
# Verificar se tem Docker
docker --version

# Verificar se tem Python 3.13+
python --version

# Verificar se tem Make (opcional)
make --version
```

## 🚀 Início Rápido (5 minutos)

### 1. Baixar e Instalar

```bash
# 1. Clone o repositório
git clone <your-repo-url>
cd evidentlyai_server

# 2. Instalar dependências Python
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou venv\Scripts\activate  # Windows

pip install -e .
```

### 2. Inicializar Servidor

```bash
# Inicializar todos os serviços
make run

# Ou usando docker-compose diretamente
docker-compose up -d
```

### 3. Verificar se Funcionou

```bash
# Verificar status
make status

# Você deve ver algo como:
# Name                     Command               State           Ports
# evidently-service        ...                  Up             0.0.0.0:8000->8000/tcp
# evidently-minio          ...                  Up             0.0.0.0:9000->9000/tcp, 0.0.0.0:9001->9001/tcp
```

### 4. Executar Primeira Demonstração

```bash
# Executar script de demo completo
python remote_demo_project.py

# Ou usar comando do Makefile
make demo
```

## 🌐 Acessando os Serviços

Após inicializar, você pode acessar:

- **EvidentlyAI Dashboard**: http://localhost:8000
- **MinIO Console**: http://localhost:9001
  - Usuário: `minioadmin` 
  - Senha: `minioadmin123`

## 📊 Exemplos de Uso

### Exemplo 1: Análise de Data Drift Rápida

```python
from examples.evidently_client import EvidentlyClient, EvidentlyOffline
from examples.data_generator import DataGenerator
import pandas as pd

# 1. Gerar dados sintéticos
generator = DataGenerator()
reference, current = generator.generate_drift_data(1000, 0.5)

# 2. Análise offline (rápida)
report = EvidentlyOffline.run_data_drift_report(
    reference, current, save_html=True, filename="meu_drift_report.html"
)

# 3. Análise no servidor (com dashboard)
client = EvidentlyClient()
project = client.create_project("Meu Projeto", "Teste de drift")
client.upload_data(project['id'], reference, "reference")
client.upload_data(project['id'], current, "current")
result = client.run_data_drift_analysis(project['id'])

print("✅ Análise concluída! Verifique o dashboard em http://localhost:8000")
```

### Exemplo 2: Monitoramento de Modelo ML

```python
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

# 1. Treinar modelo
iris = load_iris(as_frame=True)
X_train, X_test, y_train, y_test = train_test_split(
    iris.data, iris.target, test_size=0.3, random_state=42
)

model = RandomForestClassifier(random_state=42)
model.fit(X_train, y_train)

# 2. Preparar dados para monitoramento
test_data = X_test.copy()
test_data['target'] = y_test
test_data['prediction'] = model.predict(X_test)

# 3. Análise offline
EvidentlyOffline.run_classification_report(
    test_data, save_html=True, filename="model_performance.html"
)

# 4. Enviar para servidor
client = EvidentlyClient()
project = client.create_project("Modelo Iris", "Monitoramento de performance")
client.upload_data(project['id'], test_data, "current")
client.run_model_performance_analysis(project['id'], "classification")

print("📊 Relatórios salvos e enviados para o dashboard!")
```

### Exemplo 3: Avaliação de LLM

```python
import pandas as pd
from evidently import Dataset, DataDefinition
from evidently.descriptors import Sentiment, TextLength

# 1. Dados de exemplo LLM
llm_data = pd.DataFrame([
    ["What is AI?", "AI is artificial intelligence technology.", "factual"],
    ["Write a poem", "Roses are red, violets are blue...", "creative"],
    ["Help me cheat", "I can't help with dishonest activities.", "refusal"]
], columns=["question", "answer", "category"])

# 2. Criar dataset com descritores
eval_dataset = Dataset.from_pandas(
    llm_data,
    data_definition=DataDefinition(),
    descriptors=[
        Sentiment("answer", alias="Sentiment"),
        TextLength("answer", alias="Length"),
    ]
)

# 3. Gerar relatório
from evidently import Report
from evidently.presets import TextEvals

report = Report(presets=[TextEvals()])
report.run(eval_dataset)
report.save_html("llm_evaluation.html")

print("🤖 Avaliação LLM concluída!")
```

## 🔧 Comandos Úteis

```bash
# Gerenciamento dos serviços
make run          # Inicializar
make stop         # Parar
make restart      # Reinicializar
make status       # Ver status
make logs         # Ver logs

# Logs específicos
make logs-evidently    # Logs do EvidentlyAI
make logs-minio       # Logs do MinIO

# Desenvolvimento
make demo         # Executar demo completo
make clear_all    # Limpar tudo (cuidado!)
```

## 🐛 Problemas Comuns e Soluções

### ❌ Servidor não inicializa

```bash
# Verificar se portas estão livres
lsof -i :8000
lsof -i :9000
lsof -i :9001

# Parar processos conflitantes ou alterar portas no docker-compose.yaml
```

### ❌ Erro de permissões

```bash
# Linux/Mac: corrigir permissões
sudo chown -R $USER:$USER ./workspace/
chmod -R 755 ./workspace/
```

### ❌ Erro de importação

```bash
# Reinstalar dependências
pip install -e .

# Verificar se ambiente virtual está ativo
which python  # Deve apontar para venv
```

### ❌ Docker não funciona

```bash
# Verificar se Docker está rodando
docker ps

# Restart do Docker
sudo systemctl restart docker  # Linux
# ou restart Docker Desktop

# Limpar cache do Docker
docker system prune -f
```

## 🎯 Próximos Passos

1. **Explore o Dashboard**: Acesse http://localhost:8000 e navegue pelos projetos criados
2. **Teste com seus Dados**: Substitua os dados sintéticos pelos seus dados reais
3. **Customize**: Modifique os scripts para suas necessidades específicas
4. **Integre**: Use o cliente Python em seus pipelines de ML
5. **Monitore**: Configure alertas e monitoramento contínuo

## 📚 Recursos Adicionais

- **README completo**: [README.md](README.md) - Documentação detalhada
- **Exemplos**: Diretório `examples/` com scripts prontos
- **Cliente Python**: `examples/evidently_client.py` - API completa
- **Gerador de Dados**: `examples/data_generator.py` - Dados sintéticos
- **Demo Completa**: `remote_demo_project.py` - Demonstração passo a passo

## 📞 Precisa de Ajuda?

- 📖 Documentação oficial: https://docs.evidentlyai.com/
- 💬 Discord da comunidade: https://discord.gg/xZjKRaNp8b
- 🐛 Issues no GitHub: [link do seu repositório]
- 📧 Email: seu-email@exemplo.com

---

**💡 Dica**: Execute `python remote_demo_project.py` para ver todos os recursos em ação! 