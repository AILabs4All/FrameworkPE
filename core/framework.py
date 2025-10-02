from typing import Dict, Any, List, Optional
import pandas as pd
import tqdm
from pathlib import Path

from .config_loader import ConfigLoader
from .plugin_manager import PluginManager
from utils.logger import setup_logger
from utils.logger import setup_logger
from utils.file_handlers import load_data_files, save_results, validate_columns
from utils.metrics import MetricsCollector

class SecurityIncidentFramework:
    """Framework principal para classificação de incidentes de segurança."""
    
    def __init__(self, config_path: str = "config.json"):
        self.logger = setup_logger("SecurityIncidentFramework")
        self.config = ConfigLoader.load(config_path)
        self.plugin_manager = PluginManager()
        self.metrics_collector = MetricsCollector()
        
        # Valida configuração
        config_loader = ConfigLoader()
        if not config_loader.validate_config(self.config):
            raise ValueError("Configuração inválida")
        
        self.logger.info("Framework de Classificação de Incidentes de Segurança iniciado")
        
    def process_incidents(self, input_dir: str, columns: List[str], model_name: str, 
                         prompt_technique: str, output_format: str = "csv", **kwargs) -> Dict[str, Any]:
        """
        Processa incidentes de segurança usando modelo e técnica especificados.
        
        Args:
            input_dir: Diretório com arquivos de incidentes
            columns: Colunas para usar como prompt
            model_name: Nome do modelo configurado
            prompt_technique: Técnica de prompt a usar
            output_format: Formato de saída (csv, json, xlsx)
            **kwargs: Parâmetros adicionais para a técnica
            
        Returns:
            Dict com resultados e métricas
        """
        self.logger.info(f"Iniciando processamento - Modelo: {model_name}, Técnica: {prompt_technique}")
        
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
        model_config = self._get_model_config(model_name)
        if not model_config:
            raise ValueError(f"Configuração de modelo não encontrada: {model_name}")
            
        model_instance = self.plugin_manager.create_model_instance(
            model_config["plugin"], model_config
        )
        if not model_instance:
            raise ValueError(f"Erro ao criar instância do modelo: {model_name}")
        
        # Configura técnica de prompt
        prompt_config = self._get_prompt_config(prompt_technique)
        if not prompt_config:
            raise ValueError(f"Configuração de prompt não encontrada: {prompt_technique}")
            
        prompt_instance = self.plugin_manager.create_prompt_instance(
            prompt_config["plugin"], model_instance
        )
        if not prompt_instance:
            raise ValueError(f"Erro ao criar instância do prompt: {prompt_technique}")
        
        # Processa incidentes
        results = self._process_all_incidents(
            dataframes, columns, prompt_instance, prompt_config, **kwargs
        )
        
        # Salva resultados
        output_path = f"resultados_{model_name}_{prompt_technique}"
        save_results(results, output_path, output_format)
        
        # Coleta métricas finais
        performance_summary = self.metrics_collector.log_performance_summary()
        
        summary = {
            "total_incidents": len(results),
            "model_used": model_name,
            "prompt_technique": prompt_technique,
            "output_file": f"{output_path}.{output_format}",
            "performance": performance_summary
        }
        
        self.logger.info(f"Processamento concluído: {len(results)} incidentes processados")
        return summary
    
    def _process_all_incidents(self, dataframes: List[pd.DataFrame], columns: List[str], 
                              prompt_instance: Any, prompt_config: Dict[str, Any], **kwargs) -> List[Dict[str, Any]]:
        """Processa todos os incidentes dos DataFrames."""
        results = []
        total_rows = sum(len(df) for df in dataframes)
        
        # Mescla parâmetros padrão com kwargs
        params = prompt_config.get("default_params", {})
        params.update(kwargs)
        
        with tqdm.tqdm(total=total_rows, desc="Processando incidentes") as pbar:
            for df in dataframes:
                for index, row in df.iterrows():
                    # Captura o ID obrigatório da linha
                    incident_id = row.get('id')
                    if pd.isna(incident_id):
                        self.logger.warning(f"ID ausente na linha {index}, usando índice como fallback")
                        incident_id = f"row_{index}"
                    
                    # Constrói prompt
                    prompt = self._build_prompt(row, columns)
                    
                    # Executa técnica de prompt passando o ID no contexto
                    try:
                        params['incident_id'] = incident_id  # Adiciona ID aos parâmetros
                        incident_results = prompt_instance.execute(prompt, row, columns, **params)
                        
                        # Garante que cada resultado tenha o ID
                        for result in incident_results:
                            if 'id' not in result:
                                result['id'] = incident_id
                        
                        results.extend(incident_results)
                    except Exception as e:
                        self.logger.error(f"Erro ao processar incidente {incident_id}: {e}")
                        # Adiciona resultado de erro com ID
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
        """Constrói prompt base para classificação."""
        nist_enabled = self.config.get("nist_categories", {}).get("enabled", True)
        
        # Prompt base
        prompt = """
        You are a security expert.
        Categorize the following incident description into a Category and an Explanation.

        Description:
            ```"""
        
        # Adiciona informações do incidente
        for coluna in columns:
            if coluna in row and pd.notnull(row[coluna]):
                prompt += f" [{coluna}]: [{row[coluna]}]"
        
        prompt += "\n            ```"
        
        # Adiciona categorias NIST se habilitadas
        if nist_enabled:
            prompt += self._get_nist_prompt_section()
        
        return prompt
    
    def _get_nist_prompt_section(self) -> str:
        """Retorna seção do prompt com categorias NIST."""
        return """
        
        NIST Categories Available for Classification:
        - CAT1: Account Compromise – unauthorized access to user or administrator accounts.
            Examples: credential phishing, SSH brute force, OAuth token theft.
        - CAT2: Malware – infection by malicious code.
            Examples: ransomware, Trojan horse, macro virus.
        - CAT3: Denial of Service Attack – making systems unavailable.
            Examples: volumetric DoS or DDoS (UDP flood, SYN flood, HTTP, HTTPS), attack on publicly available APIs or websites, botnet Mirai attacking an institution's server.
        - CAT4: Data Leak – unauthorized disclosure of sensitive data.
            Examples: database theft, leaked credentials.
        - CAT5: Vulnerability Exploitation – using technical flaws for attacks.
            Examples: exploitation of critical CVE, remote code execution (RCE), SQL injection in web applications.
        - CAT6: Insider Abuse – malicious actions by internal users.
            Examples: copying confidential data, sabotage.
        - CAT7: Social Engineering – deception to gain access or data.
            Examples: phishing, vishing, CEO fraud.
        - CAT8: Physical Incident – impact due to unauthorized physical access.
            Examples: laptop theft, data center break-in.
        - CAT9: Unauthorized Modification – improper changes to systems or data.
            Examples: defacement, record manipulation.
        - CAT10: Misuse of Resources – unauthorized use for other purposes.
            Examples: cryptocurrency mining, malware distribution.
        - CAT11: Third-Party Issues – security failures by suppliers.
            Examples: SaaS breach, supply chain attack.
        - CAT12: Intrusion Attempt – unconfirmed attacks.
            Examples: network scans, brute force, blocked exploits.

        Your task:
        - Classify the incident below using the most appropriate category code (CAT1 to CAT12).
        - Justify based on the explanation of the selected category.
        """
    
    def _build_incident_info(self, row: pd.Series, columns: List[str]) -> str:
        """Constrói string com informações do incidente."""
        return " / ".join([
            f"{coluna}: {row[coluna]}" if coluna in row and pd.notnull(row[coluna]) 
            else f"{coluna}: [valor ausente]" 
            for coluna in columns
        ])
    
    def _get_model_config(self, model_name: str) -> Optional[Dict[str, Any]]:
        """Obtém configuração do modelo."""
        return self.config.get("models", {}).get(model_name)
    
    def _get_prompt_config(self, prompt_name: str) -> Optional[Dict[str, Any]]:
        """Obtém configuração da técnica de prompt."""
        return self.config.get("prompt_techniques", {}).get(prompt_name)
    
    def list_available_models(self) -> List[str]:
        """Lista modelos disponíveis."""
        return list(self.config.get("models", {}).keys())
    
    def list_available_prompts(self) -> List[str]:
        """Lista técnicas de prompt disponíveis."""
        return list(self.config.get("prompt_techniques", {}).keys())
    
    def get_framework_info(self) -> Dict[str, Any]:
        """Retorna informações sobre o framework."""
        return {
            "framework": self.config.get("framework", {}),
            "available_models": self.list_available_models(),
            "available_prompts": self.list_available_prompts(),
            "plugin_info": self.plugin_manager.get_plugin_info(),
            "nist_categories_enabled": self.config.get("nist_categories", {}).get("enabled", True)
        }