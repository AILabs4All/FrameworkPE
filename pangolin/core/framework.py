from typing import Dict, Any, List, Optional
import pandas as pd
import tqdm
from pathlib import Path

from .plugin_manager import PluginManager
from plugins.prompts.schema_prompt_plugin import SchemaPromptPlugin
from plugins.prompts.config import PromptConfigFactory
from .observability.logger import setup_logger
from .io.file_handlers import load_data_files, save_results, validate_columns
from .observability.metrics import MetricsCollector

class PangolinFramework:
    """Framework principal para processamento de dados com técnicas de prompt."""

    def __init__(self, project=None):
        """Inicializa framework opcionalmente com projeto isolado."""
        self.project = project

        log_dir = str(project.logs_dir) if project else "logs"
        self.logger = setup_logger("PangolinFramework", log_dir=log_dir)

        self.plugin_manager = PluginManager()

        metrics_dir = str(project.metrics_dir) if project else "logs"
        self.metrics_collector = MetricsCollector(log_dir=metrics_dir)

        self.logger.info("PangolinFramework iniciado")
        
    def process_incidents(self, input_dir: str, columns: List[str], model_config: Dict[str, Any], 
                         prompt_techniques: List[str], output_format: str = "csv", **kwargs) -> Dict[str, Any]:
        """
        Processa incidentes de segurança usando modelo e técnica especificados.
        
        Args:
            input_dir: Diretório com arquivos de incidentes
            columns: Colunas para usar como prompt
            model_config: Configuração do modelo
            prompt_techniques: Lista de técnicas de prompt a usar
            output_format: Formato de saída (csv, json, xlsx)
            **kwargs: Parâmetros adicionais para a técnica
            
        Returns:
            Dict com resultados e métricas
        """
        model_name = model_config.get('name', 'unknown')
        self.logger.info(f"Iniciando processamento - Modelo: {model_name}, Técnicas: {prompt_techniques}")
        
        # Carrega dados
        try:
            dataframes = load_data_files(input_dir)
            if not dataframes:
                raise ValueError("Nenhum arquivo de dados encontrado")
                
            # Valida colunas
            if not validate_columns(dataframes, columns):
                raise ValueError("Colunas obrigatórias não encontradas")
                
        except Exception as e:
            self.logger.error(f"Erro ao carregar dados: {e}")
            raise
        
        # Configura modelo
        provider_map = {
            'ollama': 'LocalModel',
            'local': 'LocalModel',
            'huggingface': 'HuggingfaceModel',
            'hungifface': 'HuggingfaceModel',
            'openai': 'APIModel',
            'anthropic': 'APIModel',
            'gemini': 'APIModel',
            'google': 'APIModel',
            'cohere': 'APIModel',
            'azure': 'APIModel',
            'bedrock': 'APIModel',
            'vertex': 'APIModel',
            'palm': 'APIModel'
        }
        
        provider = model_config.get('provider', '').lower()
        plugin_name = provider_map.get(provider, 'APIModel')
        
        model_instance = self.plugin_manager.create_model_instance(
            plugin_name, model_config
        )
        if not model_instance:
            raise ValueError(f"Erro ao criar instância do modelo: {model_name}")
        
        techniques = prompt_techniques

        # Processa com cada técnica e salva CSV individual
        all_results = []
        output_files = []
        for technique in techniques:
            self.logger.info(f"Processando com técnica: {technique}")

            try:
                prompt_schema = self.project.load_prompt_schema(technique)
                prompt_config = PromptConfigFactory.create(prompt_schema)
                prompt_instance = SchemaPromptPlugin(model_instance, prompt_config)
            except Exception as e:
                self.logger.warning(f"Erro ao carregar técnica de prompt '{technique}': {e}")
                continue

            # Processa incidentes
            results = self._process_all_incidents(
                dataframes, columns, prompt_instance, **kwargs
            )

            # Adiciona informação da técnica aos resultados
            for result in results:
                result['technique_used'] = technique

            # Salva CSV individual por técnica
            if self.project:
                output_path = str(self.project.get_results_path(f"resultados_{model_name}_{technique}"))
            else:
                output_path = f"resultados_{model_name}_{technique}"

            save_results(results, output_path, "csv")
            output_files.append(f"{output_path}.csv")

            all_results.extend(results)

        if not all_results:
            raise ValueError(f"Nenhum resultado foi gerado com as técnicas: {prompt_techniques}")

        # Coleta métricas finais
        performance_summary = self.metrics_collector.log_performance_summary()

        # Salva métricas no projeto se disponível
        technique_str = "_".join(techniques) if isinstance(prompt_techniques, list) else prompt_techniques
        if self.project:
            metrics_file = self.project.get_metrics_path(f"performance_{model_name}_{technique_str}.json")
            import json
            with open(metrics_file, 'w', encoding='utf-8') as f:
                json.dump(performance_summary, f, indent=2)

        summary = {
            "total_incidents": len(all_results),
            "results": all_results,
            "model_used": model_name,
            "prompt_techniques": prompt_techniques,
            "techniques_used": techniques,
            "output_files": output_files,
            "performance": performance_summary
        }
        
        self.logger.info(f"Processamento concluído: {len(all_results)} incidentes processados")
        return summary
    
    def _process_all_incidents(self, dataframes: List[pd.DataFrame], columns: List[str], 
                              prompt_instance: Any, **kwargs) -> List[Dict[str, Any]]:
        """Processa todos os incidentes dos DataFrames."""
        results = []
        total_rows = sum(len(df) for df in dataframes)
        
        with tqdm.tqdm(total=total_rows, desc="Processando incidentes") as pbar:
            for df in dataframes:
                for index, row in df.iterrows():
                    incident_id = row.get('id')
                    if pd.isna(incident_id):
                        self.logger.warning(f"ID ausente na linha {index}, usando índice como fallback")
                        incident_id = f"row_{index}"
                    
                    prompt = self._build_prompt(row, columns)
                    
                    try:
                        incident_results = prompt_instance.execute(prompt, row, columns, incident_id=incident_id, **kwargs)
                        for result in incident_results:
                            if 'id' not in result:
                                result['id'] = incident_id
                        results.extend(incident_results)
                    except Exception as e:
                        self.logger.error(f"Erro ao processar incidente {incident_id}: {e}")
                        results.append({
                            "id": incident_id,
                            "informacoes_das_colunas": self._build_incident_info(row, columns),
                            "categoria": "ERROR",
                            "explicacao": f"Erro no processamento: {str(e)}",
                            "erro": True
                        })
                    
                    pbar.update(1)
        
        return results
    
    def _build_prompt(self, row: pd.Series, columns: List[str]) -> str:
        """Constrói texto de entrada combinando as colunas configuradas."""
        parts = [
            f"[{col}]: [{row[col]}]"
            for col in columns
            if col in row and pd.notnull(row[col])
        ]
        return " ".join(parts)
    
    def _build_incident_info(self, row: pd.Series, columns: List[str]) -> str:
        """Constrói string com informações do incidente."""
        return " / ".join([
            f"{coluna}: {row[coluna]}" if coluna in row and pd.notnull(row[coluna]) 
            else f"{coluna}: [valor ausente]" 
            for coluna in columns
        ])
    

    def get_framework_info(self) -> Dict[str, Any]:
        """Retorna informações sobre o framework."""
        return {
            "framework": {"name": "Pangolin Framework", "version": "2.0.0"},
            "plugin_info": self.plugin_manager.get_plugin_info(),
        }