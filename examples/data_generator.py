"""
Gerador de Dados Sintéticos para EvidentlyAI

Este módulo fornece funções para gerar diversos tipos de dados sintéticos
para testes e demonstrações do EvidentlyAI, incluindo:
- Dados com drift temporal
- Dados com problemas de qualidade
- Dados de avaliação de LLM
- Datasets de diferentes domínios

Autor: Sua Equipe
Data: 2025
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Any, List, Tuple, Optional
import random
from faker import Faker

# Configurar faker para geração de dados
fake = Faker(['pt_BR', 'en_US'])


class DataGenerator:
    """Gerador de dados sintéticos para diferentes cenários de teste."""
    
    @staticmethod
    def generate_drift_data(n_samples: int = 1000, 
                           drift_magnitude: float = 0.5,
                           drift_type: str = "gradual") -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Gerar dados com drift artificial.
        
        Args:
            n_samples: Número de amostras por dataset
            drift_magnitude: Magnitude do drift (0-2)
            drift_type: Tipo de drift ('gradual', 'sudden', 'mixed')
            
        Returns:
            Tuple com (dados_referencia, dados_atuais)
        """
        np.random.seed(42)
        
        # Dados de referência
        reference = pd.DataFrame({
            'numeric_1': np.random.normal(0, 1, n_samples),
            'numeric_2': np.random.exponential(1, n_samples),
            'numeric_3': np.random.gamma(2, 2, n_samples),
            'categorical_1': np.random.choice(['A', 'B', 'C'], n_samples, p=[0.5, 0.3, 0.2]),
            'categorical_2': np.random.choice(['X', 'Y', 'Z'], n_samples),
            'boolean': np.random.choice([True, False], n_samples, p=[0.7, 0.3])
        })
        
        # Dados atuais com drift
        if drift_type == "gradual":
            current = pd.DataFrame({
                'numeric_1': np.random.normal(drift_magnitude, 1 + drift_magnitude*0.3, n_samples),
                'numeric_2': np.random.exponential(1 + drift_magnitude*0.5, n_samples),
                'numeric_3': np.random.gamma(2 + drift_magnitude, 2, n_samples),
                'categorical_1': np.random.choice(['A', 'B', 'C'], n_samples, 
                                                p=[0.5-drift_magnitude*0.2, 0.3, 0.2+drift_magnitude*0.2]),
                'categorical_2': np.random.choice(['X', 'Y', 'Z'], n_samples),
                'boolean': np.random.choice([True, False], n_samples, 
                                          p=[0.7-drift_magnitude*0.2, 0.3+drift_magnitude*0.2])
            })
        elif drift_type == "sudden":
            current = pd.DataFrame({
                'numeric_1': np.random.normal(drift_magnitude*2, 1, n_samples),
                'numeric_2': np.random.exponential(1, n_samples),
                'numeric_3': np.random.gamma(2, 2+drift_magnitude, n_samples),
                'categorical_1': np.random.choice(['A', 'B', 'C', 'D'], n_samples),  # Nova categoria
                'categorical_2': np.random.choice(['X', 'Y', 'Z'], n_samples),
                'boolean': np.random.choice([True, False], n_samples, p=[0.3, 0.7])
            })
        else:  # mixed
            # Combinar drifts graduais e súbitos
            current = reference.copy()
            
            # Drift gradual em algumas features
            current['numeric_1'] += drift_magnitude
            current['numeric_2'] *= (1 + drift_magnitude*0.5)
            
            # Drift súbito em outras
            mask = np.random.random(n_samples) < 0.3
            current.loc[mask, 'numeric_3'] *= 5
            
        return reference, current
    
    @staticmethod
    def generate_quality_issues_data(n_samples: int = 1000,
                                   missing_rate: float = 0.1,
                                   duplicate_rate: float = 0.05,
                                   outlier_rate: float = 0.02) -> pd.DataFrame:
        """
        Gerar dados com problemas de qualidade.
        
        Args:
            n_samples: Número de amostras
            missing_rate: Taxa de valores ausentes (0-1)
            duplicate_rate: Taxa de duplicatas (0-1)
            outlier_rate: Taxa de outliers (0-1)
            
        Returns:
            DataFrame com problemas de qualidade
        """
        np.random.seed(42)
        
        # Dados base
        data = pd.DataFrame({
            'id': range(n_samples),
            'numeric_normal': np.random.normal(50, 15, n_samples),
            'numeric_positive': np.random.exponential(5, n_samples),
            'categorical': np.random.choice(['Alpha', 'Beta', 'Gamma', 'Delta'], n_samples),
            'price': np.random.uniform(10, 1000, n_samples),
            'score': np.random.uniform(0, 100, n_samples),
            'date': pd.date_range('2023-01-01', periods=n_samples, freq='D'),
            'email': [fake.email() for _ in range(n_samples)],
            'text': [fake.text(max_nb_chars=200) for _ in range(n_samples)]
        })
        
        # Introduzir missing values
        n_missing = int(n_samples * missing_rate)
        missing_cols = ['numeric_normal', 'categorical', 'email']
        for col in missing_cols:
            missing_idx = np.random.choice(n_samples, n_missing//len(missing_cols), replace=False)
            data.loc[missing_idx, col] = None
        
        # Introduzir duplicatas
        n_duplicates = int(n_samples * duplicate_rate)
        duplicate_idx = np.random.choice(n_samples, n_duplicates, replace=False)
        duplicates = data.iloc[duplicate_idx].copy()
        duplicates['id'] = range(n_samples, n_samples + n_duplicates)  # Manter IDs únicos
        data = pd.concat([data, duplicates], ignore_index=True)
        
        # Introduzir outliers
        n_outliers = int(len(data) * outlier_rate)
        outlier_idx = np.random.choice(len(data), n_outliers, replace=False)
        
        # Outliers extremos
        data.loc[outlier_idx[:n_outliers//3], 'numeric_normal'] = np.random.uniform(200, 500, n_outliers//3)
        data.loc[outlier_idx[n_outliers//3:2*n_outliers//3], 'price'] = np.random.uniform(10000, 50000, n_outliers//3)
        data.loc[outlier_idx[2*n_outliers//3:], 'score'] = np.random.uniform(150, 300, n_outliers - 2*(n_outliers//3))
        
        # Valores inválidos
        invalid_idx = np.random.choice(len(data), 10, replace=False)
        data.loc[invalid_idx, 'score'] = -999  # Score negativo inválido
        
        return data
    

    
    @staticmethod
    def generate_time_series_data(n_days: int = 30,
                                observations_per_day: int = 100) -> pd.DataFrame:
        """
        Gerar dados de série temporal para monitoramento.
        
        Args:
            n_days: Número de dias
            observations_per_day: Observações por dia
            
        Returns:
            DataFrame com dados temporais
        """
        np.random.seed(42)
        
        start_date = datetime.now() - timedelta(days=n_days)
        dates = []
        values = []
        categories = []
        
        for day in range(n_days):
            current_date = start_date + timedelta(days=day)
            
            # Simular padrões temporais
            day_of_week = current_date.weekday()
            is_weekend = day_of_week >= 5
            
            # Base trend (crescimento ao longo do tempo)
            trend = day * 0.1
            
            # Seasonal pattern (diferença entre weekday/weekend)
            seasonal = -2 if is_weekend else 1
            
            # Noise
            for _ in range(observations_per_day):
                noise = np.random.normal(0, 1)
                value = 10 + trend + seasonal + noise
                
                dates.append(current_date + timedelta(hours=np.random.randint(0, 24)))
                values.append(value)
                categories.append('weekend' if is_weekend else 'weekday')
        
        df = pd.DataFrame({
            'timestamp': dates,
            'value': values,
            'category': categories,
            'day_of_week': [d.weekday() for d in dates],
            'hour': [d.hour for d in dates]
        })
        
        return df.sort_values('timestamp').reset_index(drop=True)
    
    @staticmethod
    def generate_model_predictions_data(n_samples: int = 1000,
                                      model_performance: str = "good") -> pd.DataFrame:
        """
        Gerar dados com predições de modelo.
        
        Args:
            n_samples: Número de amostras
            model_performance: Performance do modelo ('good', 'degraded', 'poor')
            
        Returns:
            DataFrame com features, targets e predições
        """
        np.random.seed(42)
        
        # Gerar features
        X = pd.DataFrame({
            'feature_1': np.random.normal(0, 1, n_samples),
            'feature_2': np.random.exponential(1, n_samples),
            'feature_3': np.random.uniform(-1, 1, n_samples),
            'feature_4': np.random.gamma(2, 1, n_samples),
            'categorical': np.random.choice(['A', 'B', 'C'], n_samples)
        })
        
        # Gerar targets baseados nas features (relação verdadeira)
        true_signal = (
            X['feature_1'] * 2 + 
            X['feature_2'] * 1.5 - 
            X['feature_3'] * 0.8 + 
            np.where(X['categorical'] == 'A', 1, 0) * 2
        )
        
        # Adicionar noise
        y_continuous = true_signal + np.random.normal(0, 0.5, n_samples)
        y_binary = (y_continuous > y_continuous.median()).astype(int)
        
        # Gerar predições baseadas na performance desejada
        if model_performance == "good":
            # Modelo bom: predições próximas ao target
            pred_continuous = y_continuous + np.random.normal(0, 0.2, n_samples)
            pred_proba = 1 / (1 + np.exp(-(pred_continuous - y_continuous.median())))
            pred_binary = (pred_proba > 0.5).astype(int)
            
        elif model_performance == "degraded":
            # Modelo degradado: mais noise nas predições
            pred_continuous = y_continuous + np.random.normal(0, 0.8, n_samples)
            pred_proba = 1 / (1 + np.exp(-(pred_continuous - y_continuous.median())))
            pred_proba += np.random.normal(0, 0.1, n_samples)  # Noise extra
            pred_proba = np.clip(pred_proba, 0, 1)
            pred_binary = (pred_proba > 0.5).astype(int)
            
        else:  # poor
            # Modelo ruim: predições quase aleatórias
            pred_continuous = np.random.normal(y_continuous.mean(), y_continuous.std() * 1.5, n_samples)
            pred_proba = np.random.uniform(0.2, 0.8, n_samples)
            pred_binary = np.random.choice([0, 1], n_samples)
        
        # Combinar tudo
        result = X.copy()
        result['target_continuous'] = y_continuous
        result['target_binary'] = y_binary
        result['prediction_continuous'] = pred_continuous
        result['prediction_binary'] = pred_binary
        result['prediction_proba'] = pred_proba
        result['timestamp'] = pd.date_range('2024-01-01', periods=n_samples, freq='1H')
        
        return result


def generate_synthetic_data() -> pd.DataFrame:
    """
    Função de conveniência para gerar dados sintéticos rápidos.
    
    Returns:
        DataFrame com dados sintéticos variados
    """
    generator = DataGenerator()
    
    # Combinar diferentes tipos de dados
    reference, current = generator.generate_drift_data(500, 0.3)
    quality_data = generator.generate_quality_issues_data(300, 0.05, 0.02, 0.01)
    
    # Adicionar timestamp
    reference['timestamp'] = pd.date_range('2024-01-01', periods=len(reference), freq='1H')
    current['timestamp'] = pd.date_range('2024-01-15', periods=len(current), freq='1H')
    
    # Marcar origem dos dados
    reference['data_source'] = 'reference'
    current['data_source'] = 'current'
    
    # Combinar
    combined = pd.concat([reference, current], ignore_index=True)
    
    return combined.sort_values('timestamp').reset_index(drop=True)


if __name__ == "__main__":
    # Teste das funções de geração
    print("🧪 Testando gerador de dados sintéticos...")
    
    generator = DataGenerator()
    
    print("\n1. Dados com drift:")
    ref, curr = generator.generate_drift_data(100, 0.5)
    print(f"Referência: {ref.shape}, Atual: {curr.shape}")
    
    print("\n2. Dados com problemas de qualidade:")
    quality = generator.generate_quality_issues_data(100)
    print(f"Dados problemáticos: {quality.shape}")
    print(f"Missing values: {quality.isnull().sum().sum()}")
    
    print("\n3. Dados de série temporal:")
    ts_data = generator.generate_time_series_data(7, 10)
    print(f"Dados temporais: {ts_data.shape}")
    
    print("\n4. Dados de predições:")
    pred_data = generator.generate_model_predictions_data(100, "good")
    print(f"Dados de predições: {pred_data.shape}")
    
    print("\n✅ Todos os geradores funcionando corretamente!") 