import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

def setup_logger(name: str, log_level: str = "INFO", log_dir: str = "logs") -> logging.Logger:
    """
    Configura e retorna um logger personalizado.
    
    Args:
        name: Nome do logger
        log_level: Nível de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_dir: Diretório para salvar os logs
    
    Returns:
        logging.Logger: Logger configurado
    """
    # Cria o diretório de logs se não existir
    Path(log_dir).mkdir(parents=True, exist_ok=True)
    
    # Cria o logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Remove handlers existentes para evitar duplicação
    logger.handlers.clear()
    
    # Formatter para os logs
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Handler para arquivo
    log_file = Path(log_dir) / f"{name}_{datetime.now().strftime('%Y%m%d')}.log"
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Handler para console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger

class FrameworkLogger:
    def __init__(self, log_dir="logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        self.logger = setup_logger("FrameworkLogger")
    
    def log_interaction(self, model_name, prompt_technique, input_tokens, output_tokens, prompt, response, incident_id=None):
        """Registra interação com modelo."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "model_name": model_name,
            "prompt_technique": prompt_technique,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "prompt": prompt,
            "response": response
        }
        
        # Adiciona ID do incidente se fornecido
        if incident_id is not None:
            log_entry["id"] = incident_id
        
        # Nome do arquivo baseado na data, modelo e técnica
        date_str = datetime.now().strftime("%Y-%m-%d")
        filename = f"{date_str}_{model_name.replace('/', '-')}_{prompt_technique}.json"
        log_file = self.log_dir / filename
        
        # Carrega logs existentes ou cria nova lista
        logs = []
        if log_file.exists():
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
            except Exception as e:
                self.logger.warning(f"Erro ao carregar log existente: {e}")
                logs = []
        
        # Adiciona nova entrada
        logs.append(log_entry)
        
        # Salva logs atualizados
        try:
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(logs, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.logger.error(f"Erro ao salvar log: {e}")
    
    def get_logs_summary(self) -> dict:
        """Retorna resumo dos logs."""
        summary = {
            "total_interactions": 0,
            "models_used": set(),
            "techniques_used": set(),
            "total_input_tokens": 0,
            "total_output_tokens": 0
        }
        
        for log_file in self.log_dir.glob("*.json"):
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
                    for log in logs:
                        summary["total_interactions"] += 1
                        summary["models_used"].add(log.get("model_name", "unknown"))
                        summary["techniques_used"].add(log.get("prompt_technique", "unknown"))
                        summary["total_input_tokens"] += log.get("input_tokens", 0)
                        summary["total_output_tokens"] += log.get("output_tokens", 0)
            except Exception as e:
                self.logger.warning(f"Erro ao processar arquivo de log {log_file}: {e}")
        
        # Converte sets para listas para serialização JSON
        summary["models_used"] = list(summary["models_used"])
        summary["techniques_used"] = list(summary["techniques_used"])
        
        return summary