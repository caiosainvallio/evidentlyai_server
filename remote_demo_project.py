#!/usr/bin/env python3
"""
Script Principal de Demonstração - EvidentlyAI Server

Este script demonstra como usar o servidor EvidentlyAI para:
1. Monitoramento de Data Drift
2. Avaliação de Performance de Modelos ML
3. Verificação de Qualidade de Dados
4. Integração com pipelines de ML

Execute este script após inicializar o servidor com: make run

Autor: Sua Equipe
Data: 2025
"""

import sys
import time
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.datasets import load_iris, make_classification
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
import warnings

# Adicionar diretório de exemplos ao path
sys.path.append(str(Path(__file__).parent / "examples"))

try:
    from examples.evidently_client import EvidentlyClient, EvidentlyOffline
    from evidently import Report, Dataset, DataDefinition
    from evidently.presets import (
        DataDriftPreset, ClassificationPreset, 
        DataQualityPreset
    )
except ImportError as e:
    print(f"❌ Erro de importação: {e}")
    print("📦 Instale as dependências com: pip install -e .")
    sys.exit(1)

warnings.filterwarnings('ignore')


class EvidentlyDemo:
    """Classe principal para demonstrações do EvidentlyAI."""
    
    def __init__(self, server_url: str = "http://localhost:8000"):
        """Inicializar demo com cliente EvidentlyAI."""
        self.client = EvidentlyClient(base_url=server_url)
        self.project_ids = {}
        print(f"🚀 Iniciando demo do EvidentlyAI Server")
        print(f"🔗 Servidor: {server_url}")
        print("-" * 60)
    
    def check_server_health(self) -> bool:
        """Verificar se servidor está funcionando."""
        print("🏥 Verificando saúde do servidor...")
        health = self.client.health_check()
        
        if health['status'] == 'healthy':
            print("✅ Servidor está funcionando!")
            return True
        else:
            print(f"❌ Servidor não está funcionando: {health.get('error', 'Erro desconhecido')}")
            print("💡 Dica: Execute 'make run' para inicializar o servidor")
            return False
    
    def demo_1_data_drift_detection(self):
        """Demo 1: Detecção de Data Drift."""
        print("\n" + "="*60)
        print("📊 DEMO 1: DETECÇÃO DE DATA DRIFT")
        print("="*60)
        
        # 1. Criar dados sintéticos
        print("📈 Gerando dados sintéticos...")
        np.random.seed(42)
        
        # Dados de referência (distribuição normal)
        reference_data = pd.DataFrame({
            'feature_1': np.random.normal(0, 1, 1000),
            'feature_2': np.random.normal(5, 2, 1000),
            'feature_3': np.random.exponential(1, 1000),
            'categorical': np.random.choice(['A', 'B', 'C'], 1000)
        })
        
        # Dados atuais (com drift - distribuição alterada)
        current_data = pd.DataFrame({
            'feature_1': np.random.normal(0.5, 1.2, 1000),  # Drift na média e desvio
            'feature_2': np.random.normal(5.5, 1.8, 1000),  # Drift leve
            'feature_3': np.random.exponential(1.5, 1000),   # Drift na distribuição
            'categorical': np.random.choice(['A', 'B', 'C', 'D'], 1000)  # Nova categoria
        })
        
        print(f"📋 Dados de referência: {reference_data.shape}")
        print(f"📋 Dados atuais: {current_data.shape}")
        
        # 2. Executar análise offline (desenvolvimento/teste)
        print("\n🔬 Executando análise offline...")
        offline_report = EvidentlyOffline.run_data_drift_report(
            reference_data=reference_data,
            current_data=current_data,
            save_html=True,
            filename="reports/data_drift_offline.html"
        )
        print("💾 Relatório offline salvo em: reports/data_drift_offline.html")
        
        # 3. Criar projeto no servidor
        try:
            print("\n🏗️  Criando projeto no servidor...")
            project = self.client.create_project(
                name="Data Drift Analysis Demo",
                description="Demonstração de detecção de data drift em dados sintéticos"
            )
            project_id = project.get('id')
            self.project_ids['data_drift'] = project_id
            print(f"✅ Projeto criado com ID: {project_id}")
            
            # 4. Upload dos dados
            print("📤 Enviando dados para o servidor...")
            self.client.upload_data(project_id, reference_data, "reference")
            self.client.upload_data(project_id, current_data, "current")
            print("✅ Dados enviados com sucesso!")
            
            # 5. Executar análise no servidor
            print("🔍 Executando análise de data drift...")
            drift_analysis = self.client.run_data_drift_analysis(
                project_id,
                config={"method": "psi", "threshold": 0.1}
            )
            print("✅ Análise de drift executada!")
            
            # 6. Obter resultados
            if 'report_id' in drift_analysis:
                report_id = drift_analysis['report_id']
                print(f"📊 ID do relatório: {report_id}")
                
                # Salvar relatório HTML
                success = self.client.save_report_html(
                    project_id, report_id, "reports/data_drift_server.html"
                )
                if success:
                    print("💾 Relatório do servidor salvo em: reports/data_drift_server.html")
            
        except Exception as e:
            print(f"⚠️  Erro no servidor: {e}")
            print("💡 Usando apenas análise offline...")
    
    def demo_2_ml_model_monitoring(self):
        """Demo 2: Monitoramento de Performance de Modelo ML."""
        print("\n" + "="*60)
        print("🤖 DEMO 2: MONITORAMENTO DE MODELO ML")
        print("="*60)
        
        # 1. Criar e treinar modelo
        print("🎯 Criando modelo de classificação...")
        iris = load_iris(as_frame=True)
        X, y = iris.data, iris.target
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.3, random_state=42, stratify=y
        )
        
        # Treinar modelo
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        
        # Fazer predições
        predictions = model.predict(X_test)
        probabilities = model.predict_proba(X_test)
        
        accuracy = accuracy_score(y_test, predictions)
        print(f"🎯 Accuracy do modelo: {accuracy:.3f}")
        
        # 2. Preparar dados para avaliação
        test_data = X_test.copy()
        test_data['target'] = y_test
        test_data['prediction'] = predictions
        
        # Adicionar probabilidades
        for i, class_name in enumerate(iris.target_names):
            test_data[f'prob_{class_name}'] = probabilities[:, i]
        
        train_data = X_train.copy()
        train_data['target'] = y_train
        train_predictions = model.predict(X_train)
        train_data['prediction'] = train_predictions
        
        print(f"📋 Dados de teste preparados: {test_data.shape}")
        
        # 3. Análise offline
        print("\n🔬 Executando análise offline...")
        offline_report = EvidentlyOffline.run_classification_report(
            data=test_data,
            save_html=True,
            filename="reports/model_performance_offline.html"
        )
        print("💾 Relatório offline salvo em: reports/model_performance_offline.html")
        
        # 4. Análise no servidor
        try:
            print("\n🏗️  Criando projeto no servidor...")
            project = self.client.create_project(
                name="ML Model Performance Demo",
                description="Monitoramento de performance do modelo Iris"
            )
            project_id = project.get('id')
            self.project_ids['model_performance'] = project_id
            
            # Upload dos dados
            print("📤 Enviando dados para o servidor...")
            self.client.upload_data(project_id, train_data, "reference")
            self.client.upload_data(project_id, test_data, "current")
            
            # Análise de performance
            print("🔍 Executando análise de performance...")
            perf_analysis = self.client.run_model_performance_analysis(
                project_id, "classification"
            )
            print("✅ Análise de performance executada!")
            
            # Data drift entre treino e teste
            print("🔍 Verificando data drift...")
            drift_analysis = self.client.run_data_drift_analysis(project_id)
            print("✅ Análise de drift executada!")
            
        except Exception as e:
            print(f"⚠️  Erro no servidor: {e}")
    
    def demo_3_data_quality_check(self):
        """Demo 3: Verificação de Qualidade dos Dados."""
        print("\n" + "="*60)
        print("🔍 DEMO 3: VERIFICAÇÃO DE QUALIDADE DOS DADOS")
        print("="*60)
        
        # 1. Criar dados com problemas de qualidade
        print("📊 Gerando dados com problemas de qualidade...")
        np.random.seed(42)
        
        n_samples = 1000
        data = pd.DataFrame({
            'numeric_1': np.random.normal(10, 3, n_samples),
            'numeric_2': np.random.exponential(2, n_samples),
            'categorical': np.random.choice(['A', 'B', 'C', 'D'], n_samples),
            'text_column': [f"Text sample {i}" for i in range(n_samples)],
            'date_column': pd.date_range('2023-01-01', periods=n_samples, freq='D')
        })
        
        # Introduzir problemas de qualidade
        # Missing values
        missing_indices = np.random.choice(n_samples, 50, replace=False)
        data.loc[missing_indices, 'numeric_1'] = None
        
        # Duplicatas
        data = pd.concat([data, data.iloc[:20]], ignore_index=True)
        
        # Outliers extremos
        outlier_indices = np.random.choice(len(data), 10, replace=False)
        data.loc[outlier_indices, 'numeric_2'] = data['numeric_2'].max() * 10
        
        # Valores fora do range esperado
        data.loc[data.index[:15], 'numeric_1'] = -999  # Valor impossível
        
        print(f"📋 Dados com problemas: {data.shape}")
        print(f"🔢 Missing values: {data.isnull().sum().sum()}")
        print(f"🔄 Duplicatas: {data.duplicated().sum()}")
        
        # 2. Análise offline
        print("\n🔬 Executando verificação de qualidade offline...")
        try:
            from evidently import Report
            from evidently.presets import DataQualityPreset
            
            quality_report = Report(presets=[DataQualityPreset()])
            quality_report.run(reference_data=None, current_data=data)
            quality_report.save_html("reports/data_quality_offline.html")
            print("💾 Relatório offline salvo em: reports/data_quality_offline.html")
        except Exception as e:
            print(f"⚠️  Erro na análise offline: {e}")
        
        # 3. Análise no servidor
        try:
            print("\n🏗️  Criando projeto no servidor...")
            project = self.client.create_project(
                name="Data Quality Check Demo",
                description="Verificação de qualidade em dados com problemas"
            )
            project_id = project.get('id')
            self.project_ids['data_quality'] = project_id
            
            # Upload dos dados
            print("📤 Enviando dados para o servidor...")
            self.client.upload_data(project_id, data, "current")
            
            # Análise de qualidade
            print("🔍 Executando verificação de qualidade...")
            quality_analysis = self.client.run_data_quality_check(project_id)
            print("✅ Verificação de qualidade executada!")
            
        except Exception as e:
            print(f"⚠️  Erro no servidor: {e}")
    
    def demo_4_comprehensive_monitoring(self):
        """Demo 4: Monitoramento Abrangente."""
        print("\n" + "="*60)
        print("📊 DEMO 4: MONITORAMENTO ABRANGENTE")
        print("="*60)
        
        # 1. Simular pipeline de ML em produção
        print("🏭 Simulando pipeline de ML em produção...")
        
        # Criar dados históricos (baseline)
        X_baseline, y_baseline = make_classification(
            n_samples=5000, n_features=20, n_classes=3,
            n_informative=15, n_redundant=5, random_state=42
        )
        
        # Simular dados de produção (com drift gradual)
        X_production, y_production = make_classification(
            n_samples=1000, n_features=20, n_classes=3,
            n_informative=15, n_redundant=5, random_state=123  # Seed diferente
        )
        
        # Adicionar drift artificial
        X_production = X_production + np.random.normal(0, 0.3, X_production.shape)
        
        # Treinar modelo no baseline
        model = LogisticRegression(random_state=42, max_iter=1000)
        model.fit(X_baseline, y_baseline)
        
        # Predições em produção
        y_pred_production = model.predict(X_production)
        y_prob_production = model.predict_proba(X_production)
        
        # Preparar dados
        feature_names = [f'feature_{i}' for i in range(20)]
        
        baseline_df = pd.DataFrame(X_baseline, columns=feature_names)
        baseline_df['target'] = y_baseline
        baseline_df['prediction'] = model.predict(X_baseline)
        
        production_df = pd.DataFrame(X_production, columns=feature_names)
        production_df['target'] = y_production  # Em produção, nem sempre temos
        production_df['prediction'] = y_pred_production
        
        print(f"📊 Dados baseline: {baseline_df.shape}")
        print(f"📊 Dados produção: {production_df.shape}")
        
        # 2. Análise abrangente
        print("\n🔍 Executando monitoramento abrangente...")
        
        try:
            project = self.client.create_project(
                name="Comprehensive Monitoring Demo",
                description="Monitoramento completo de sistema ML em produção"
            )
            project_id = project.get('id')
            self.project_ids['comprehensive'] = project_id
            
            # Upload dos dados
            print("📤 Enviando dados baseline e produção...")
            self.client.upload_data(project_id, baseline_df, "reference")
            self.client.upload_data(project_id, production_df, "current")
            
            # Executar todas as análises
            analyses = {}
            
            print("🔍 1. Análise de Data Drift...")
            analyses['drift'] = self.client.run_data_drift_analysis(project_id)
            
            print("🔍 2. Análise de Performance...")
            analyses['performance'] = self.client.run_model_performance_analysis(
                project_id, "classification"
            )
            
            print("🔍 3. Verificação de Qualidade...")
            analyses['quality'] = self.client.run_data_quality_check(project_id)
            
            print("✅ Todas as análises executadas!")
            
            # Obter métricas consolidadas
            print("\n📊 Obtendo métricas consolidadas...")
            metrics = self.client.get_project_metrics(project_id, "all")
            
            if metrics:
                print("🎯 Resumo das métricas:")
                for key, value in metrics.items():
                    if isinstance(value, (int, float)):
                        print(f"  {key}: {value:.3f}")
            
        except Exception as e:
            print(f"⚠️  Erro no monitoramento abrangente: {e}")
    
    def display_summary(self):
        """Exibir resumo dos projetos criados."""
        print("\n" + "="*60)
        print("📋 RESUMO DOS PROJETOS CRIADOS")
        print("="*60)
        
        if not self.project_ids:
            print("❌ Nenhum projeto foi criado no servidor.")
            return
        
        print("🎯 Acesse o dashboard em: http://localhost:8000")
        print("\n📊 Projetos criados:")
        
        for demo_name, project_id in self.project_ids.items():
            print(f"  🔹 {demo_name}: {project_id}")
        
        print("\n📁 Relatórios HTML salvos em:")
        print("  🔹 reports/data_drift_offline.html")
        print("  🔹 reports/model_performance_offline.html")
        print("  🔹 reports/data_quality_offline.html")
        
        print("\n💡 Próximos passos:")
        print("  1. Acesse o dashboard web em http://localhost:8000")
        print("  2. Explore os relatórios HTML gerados")
        print("  3. Teste a API usando examples/evidently_client.py")
        print("  4. Integre com seus próprios dados e modelos")
    
    def run_all_demos(self):
        """Executar todas as demonstrações."""
        # Verificar servidor
        if not self.check_server_health():
            print("\n💡 Executando apenas demos offline...")
            print("Para usar o servidor, execute: make run")
        
        # Criar diretório para relatórios
        Path("reports").mkdir(exist_ok=True)
        
        # Executar demos
        self.demo_1_data_drift_detection()
        time.sleep(2)  # Pausa entre demos
        
        self.demo_2_ml_model_monitoring()
        time.sleep(2)
        
        self.demo_3_data_quality_check()
        time.sleep(2)
        
        self.demo_4_comprehensive_monitoring()
        
        # Resumo final
        self.display_summary()


def main():
    """Função principal do script de demonstração."""
    print("🎬 EVIDENTLY AI SERVER - DEMONSTRAÇÃO COMPLETA")
    print("=" * 60)
    print("Este script demonstra todas as funcionalidades principais")
    print("do servidor EvidentlyAI para monitoramento de ML.")
    print("=" * 60)
    
    # Criar e executar demo
    demo = EvidentlyDemo()
    
    try:
        demo.run_all_demos()
        print("\n🎉 Demonstração concluída com sucesso!")
        
    except KeyboardInterrupt:
        print("\n⏹️  Demonstração interrompida pelo usuário.")
        
    except Exception as e:
        print(f"\n❌ Erro durante a demonstração: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        print("\n👋 Obrigado por usar o EvidentlyAI!")


if __name__ == "__main__":
    main() 