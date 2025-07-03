"""
Cliente Python para EvidentlyAI Server

Este módulo fornece uma interface Python simplificada para interagir
com o servidor EvidentlyAI via API REST.

Autor: Sua Equipe
Data: 2025
"""

import json
import uuid
import requests
import pandas as pd
from typing import Dict, Any, Optional, List, Union
from pathlib import Path
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EvidentlyClient:
    """
    Cliente para interagir com o servidor EvidentlyAI.
    
    Funcionalidades:
    - Criar e gerenciar projetos
    - Fazer upload de dados
    - Executar relatórios e avaliações
    - Monitorar performance de modelos
    - Obter resultados de análises
    """
    
    def __init__(self, base_url: str = "http://localhost:8000", timeout: int = 30):
        """
        Inicializar cliente EvidentlyAI.
        
        Args:
            base_url: URL base do servidor EvidentlyAI
            timeout: Timeout para requisições HTTP em segundos
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        self.session.timeout = timeout
        
        # Headers padrão
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'EvidentlyAI-Python-Client/1.0'
        })
        
    def health_check(self) -> Dict[str, Any]:
        """
        Verificar se o servidor está funcionando.
        
        Returns:
            Dict com status do servidor
        """
        try:
            response = self.session.get(f"{self.base_url}/api/health")
            response.raise_for_status()
            return {"status": "healthy", "response": response.json()}
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro na verificação de saúde: {e}")
            return {"status": "unhealthy", "error": str(e)}
    
    def create_project(self, name: str, description: str = "") -> Dict[str, Any]:
        """
        Criar novo projeto no EvidentlyAI.
        
        Args:
            name: Nome do projeto
            description: Descrição do projeto
            
        Returns:
            Dados do projeto criado
        """
        payload = {
            "name": name,
            "description": description,
            "id": str(uuid.uuid4()),
            "created_at": datetime.now().isoformat()
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/projects",
                json=payload
            )
            response.raise_for_status()
            logger.info(f"Projeto '{name}' criado com sucesso!")
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao criar projeto: {e}")
            raise
    
    def list_projects(self) -> List[Dict[str, Any]]:
        """
        Listar todos os projetos.
        
        Returns:
            Lista de projetos
        """
        try:
            response = self.session.get(f"{self.base_url}/api/projects")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao listar projetos: {e}")
            return []
    
    def get_project(self, project_id: str) -> Optional[Dict[str, Any]]:
        """
        Obter detalhes de um projeto específico.
        
        Args:
            project_id: ID do projeto
            
        Returns:
            Dados do projeto ou None se não encontrado
        """
        try:
            response = self.session.get(f"{self.base_url}/api/projects/{project_id}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao obter projeto {project_id}: {e}")
            return None
    
    def upload_data(self, project_id: str, data: pd.DataFrame, 
                   data_type: str = "reference") -> Dict[str, Any]:
        """
        Fazer upload de dados para um projeto.
        
        Args:
            project_id: ID do projeto
            data: DataFrame com os dados
            data_type: Tipo dos dados ('reference' ou 'current')
            
        Returns:
            Resposta do servidor
        """
        # Converter DataFrame para CSV
        csv_data = data.to_csv(index=False)
        
        # Preparar arquivo para upload
        files = {
            'file': (f'{data_type}_data.csv', csv_data, 'text/csv')
        }
        
        try:
            # Remover Content-Type header para multipart/form-data
            headers = {k: v for k, v in self.session.headers.items() 
                      if k.lower() != 'content-type'}
            
            response = self.session.post(
                f"{self.base_url}/api/projects/{project_id}/data/{data_type}",
                files=files,
                headers=headers
            )
            response.raise_for_status()
            logger.info(f"Dados {data_type} enviados para projeto {project_id}")
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao enviar dados: {e}")
            raise
    
    def run_data_drift_analysis(self, project_id: str, 
                               config: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Executar análise de data drift.
        
        Args:
            project_id: ID do projeto
            config: Configurações adicionais
            
        Returns:
            Resultado da análise
        """
        payload = {
            "preset": "DataDriftPreset",
            "config": config or {"method": "psi", "threshold": 0.1}
        }
        
        return self._run_analysis(project_id, "data_drift", payload)
    
    def run_model_performance_analysis(self, project_id: str,
                                     model_type: str = "classification",
                                     config: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Executar análise de performance do modelo.
        
        Args:
            project_id: ID do projeto
            model_type: Tipo do modelo ('classification', 'regression', etc.)
            config: Configurações adicionais
            
        Returns:
            Resultado da análise
        """
        preset_map = {
            "classification": "ClassificationPreset",
            "regression": "RegressionPreset",
            "ranking": "RankingPreset"
        }
        
        payload = {
            "preset": preset_map.get(model_type, "ClassificationPreset"),
            "config": config or {}
        }
        
        return self._run_analysis(project_id, "model_performance", payload)
    
    def run_data_quality_check(self, project_id: str,
                              config: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Executar verificação de qualidade dos dados.
        
        Args:
            project_id: ID do projeto
            config: Configurações adicionais
            
        Returns:
            Resultado da verificação
        """
        payload = {
            "preset": "DataQualityPreset",
            "config": config or {}
        }
        
        return self._run_analysis(project_id, "data_quality", payload)
    
    def run_llm_evaluation(self, project_id: str,
                          config: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Executar avaliação de LLM.
        
        Args:
            project_id: ID do projeto
            config: Configurações adicionais
            
        Returns:
            Resultado da avaliação
        """
        payload = {
            "preset": "TextEvals",
            "config": config or {
                "descriptors": ["Sentiment", "TextLength", "Toxicity"]
            }
        }
        
        return self._run_analysis(project_id, "llm_evaluation", payload)
    
    def _run_analysis(self, project_id: str, analysis_type: str,
                     payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executar análise genérica.
        
        Args:
            project_id: ID do projeto
            analysis_type: Tipo da análise
            payload: Dados da requisição
            
        Returns:
            Resultado da análise
        """
        try:
            response = self.session.post(
                f"{self.base_url}/api/projects/{project_id}/reports/{analysis_type}",
                json=payload
            )
            response.raise_for_status()
            logger.info(f"Análise {analysis_type} executada para projeto {project_id}")
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao executar análise {analysis_type}: {e}")
            raise
    
    def get_report(self, project_id: str, report_id: str) -> Optional[Dict[str, Any]]:
        """
        Obter relatório específico.
        
        Args:
            project_id: ID do projeto
            report_id: ID do relatório
            
        Returns:
            Dados do relatório ou None se não encontrado
        """
        try:
            response = self.session.get(
                f"{self.base_url}/api/projects/{project_id}/reports/{report_id}"
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao obter relatório {report_id}: {e}")
            return None
    
    def list_reports(self, project_id: str) -> List[Dict[str, Any]]:
        """
        Listar todos os relatórios de um projeto.
        
        Args:
            project_id: ID do projeto
            
        Returns:
            Lista de relatórios
        """
        try:
            response = self.session.get(
                f"{self.base_url}/api/projects/{project_id}/reports"
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao listar relatórios: {e}")
            return []
    
    def export_report(self, project_id: str, report_id: str,
                     format: str = "json") -> Union[Dict, str]:
        """
        Exportar relatório em formato específico.
        
        Args:
            project_id: ID do projeto
            report_id: ID do relatório
            format: Formato de exportação ('json', 'html')
            
        Returns:
            Dados do relatório no formato especificado
        """
        try:
            response = self.session.get(
                f"{self.base_url}/api/projects/{project_id}/reports/{report_id}/export",
                params={"format": format}
            )
            response.raise_for_status()
            
            if format == "json":
                return response.json()
            else:
                return response.text
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao exportar relatório: {e}")
            raise
    
    def save_report_html(self, project_id: str, report_id: str,
                        filename: str) -> bool:
        """
        Salvar relatório como arquivo HTML.
        
        Args:
            project_id: ID do projeto
            report_id: ID do relatório
            filename: Nome do arquivo para salvar
            
        Returns:
            True se salvo com sucesso, False caso contrário
        """
        try:
            html_content = self.export_report(project_id, report_id, "html")
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"Relatório salvo como {filename}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao salvar relatório HTML: {e}")
            return False
    
    def delete_project(self, project_id: str) -> bool:
        """
        Deletar projeto.
        
        Args:
            project_id: ID do projeto
            
        Returns:
            True se deletado com sucesso, False caso contrário
        """
        try:
            response = self.session.delete(f"{self.base_url}/api/projects/{project_id}")
            response.raise_for_status()
            logger.info(f"Projeto {project_id} deletado com sucesso")
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao deletar projeto: {e}")
            return False
    
    def get_project_metrics(self, project_id: str,
                           metric_type: str = "all") -> Dict[str, Any]:
        """
        Obter métricas consolidadas de um projeto.
        
        Args:
            project_id: ID do projeto
            metric_type: Tipo de métrica ('drift', 'performance', 'quality', 'all')
            
        Returns:
            Métricas consolidadas
        """
        try:
            response = self.session.get(
                f"{self.base_url}/api/projects/{project_id}/metrics",
                params={"type": metric_type}
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao obter métricas: {e}")
            return {}


# Classe de conveniência para operações offline
class EvidentlyOffline:
    """
    Classe para executar análises Evidently offline (sem servidor).
    Útil para desenvolvimento e testes.
    """
    
    @staticmethod
    def run_data_drift_report(reference_data: pd.DataFrame,
                             current_data: pd.DataFrame,
                             save_html: bool = True,
                             filename: str = "data_drift_report.html"):
        """
        Executar relatório de data drift offline.
        
        Args:
            reference_data: Dados de referência
            current_data: Dados atuais
            save_html: Se deve salvar como HTML
            filename: Nome do arquivo HTML
            
        Returns:
            Objeto Report do Evidently
        """
        from evidently import Report
        from evidently.presets import DataDriftPreset
        
        report = Report(presets=[DataDriftPreset()])
        report.run(reference_data=reference_data, current_data=current_data)
        
        if save_html:
            report.save_html(filename)
            logger.info(f"Relatório salvo como {filename}")
        
        return report
    
    @staticmethod
    def run_classification_report(data: pd.DataFrame,
                                 target_col: str = "target",
                                 prediction_col: str = "prediction",
                                 save_html: bool = True,
                                 filename: str = "classification_report.html"):
        """
        Executar relatório de classificação offline.
        
        Args:
            data: DataFrame com dados, target e predições
            target_col: Nome da coluna target
            prediction_col: Nome da coluna de predições
            save_html: Se deve salvar como HTML
            filename: Nome do arquivo HTML
            
        Returns:
            Objeto Report do Evidently
        """
        from evidently import Report
        from evidently.presets import ClassificationPreset
        
        report = Report(presets=[ClassificationPreset()])
        report.run(reference_data=None, current_data=data)
        
        if save_html:
            report.save_html(filename)
            logger.info(f"Relatório salvo como {filename}")
        
        return report


if __name__ == "__main__":
    # Exemplo de uso básico
    client = EvidentlyClient()
    
    # Verificar se servidor está funcionando
    health = client.health_check()
    print(f"Status do servidor: {health['status']}")
    
    if health['status'] == 'healthy':
        # Criar projeto de teste
        project = client.create_project(
            name="Teste API Client",
            description="Projeto de teste para demonstrar o cliente Python"
        )
        print(f"Projeto criado: {project}")
        
        # Listar projetos
        projects = client.list_projects()
        print(f"Total de projetos: {len(projects)}") 