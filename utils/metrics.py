import time
import psutil
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from utils.logger import setup_logger

class TokenMetrics:
    """Classe para coletar e gerenciar métricas de tokens e performance."""
    
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.logger = setup_logger("TokenMetrics")
        self.interactions = []
        
    def log_interaction(self, model_name: str, mode: str, input_tokens: int, 
                       output_tokens: int, prompt: str, response: str, incident_id: Optional[str] = None):
        """Registra uma interação com o modelo."""
        interaction = {
            "timestamp": datetime.now().isoformat(),
            "model_name": model_name,
            "mode": mode,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": input_tokens + output_tokens,
            "prompt": prompt,
            "response": response
        }
        
        # Adiciona ID do incidente se fornecido
        if incident_id is not None:
            interaction["id"] = incident_id
        
        self.interactions.append(interaction)
        self._save_to_file(interaction, model_name, mode)
        
    def _save_to_file(self, interaction: dict, model_name: str, mode: str):
        """Salva interação em arquivo JSON."""
        date_str = datetime.now().strftime("%Y-%m-%d")
        filename = f"{date_str}_{model_name.replace('/', '-')}_{mode}.json"
        filepath = self.log_dir / filename
        
        # Carrega dados existentes
        data = []
        if filepath.exists():
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except Exception as e:
                self.logger.warning(f"Erro ao carregar arquivo de métricas: {e}")
                
        # Adiciona nova interação
        data.append(interaction)
        
        # Salva dados atualizados
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.logger.error(f"Erro ao salvar métricas: {e}")
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Retorna resumo da sessão atual."""
        if not self.interactions:
            return {"message": "Nenhuma interação registrada"}
            
        total_input = sum(i["input_tokens"] for i in self.interactions)
        total_output = sum(i["output_tokens"] for i in self.interactions)
        models_used = set(i["model_name"] for i in self.interactions)
        modes_used = set(i["mode"] for i in self.interactions)
        
        return {
            "total_interactions": len(self.interactions),
            "total_input_tokens": total_input,
            "total_output_tokens": total_output,
            "total_tokens": total_input + total_output,
            "average_input_tokens": total_input / len(self.interactions),
            "average_output_tokens": total_output / len(self.interactions),
            "models_used": list(models_used),
            "modes_used": list(modes_used),
            "first_interaction": self.interactions[0]["timestamp"],
            "last_interaction": self.interactions[-1]["timestamp"]
        }

class MetricsCollector:
    """Coletor de métricas de performance do sistema."""
    
    def __init__(self):
        self.start_time = time.time()
        self.process = psutil.Process()
        self.initial_memory = self.process.memory_info().rss / (1024 * 1024)  # MB
        self.logger = setup_logger("MetricsCollector")
    
    def get_memory_usage(self) -> float:
        """Retorna uso atual de memória em MB."""
        return self.process.memory_info().rss / (1024 * 1024)  # MB
    
    def get_execution_time(self) -> float:
        """Retorna tempo de execução em segundos."""
        return time.time() - self.start_time
    
    def get_memory_delta(self) -> float:
        """Retorna diferença de memória desde o início em MB."""
        return self.get_memory_usage() - self.initial_memory
    
    def log_performance_summary(self):
        """Registra resumo de performance."""
        summary = {
            "execution_time_seconds": self.get_execution_time(),
            "initial_memory_mb": self.initial_memory,
            "final_memory_mb": self.get_memory_usage(),
            "memory_delta_mb": self.get_memory_delta(),
            "timestamp": datetime.now().isoformat()
        }
        
        self.logger.info(f"Performance Summary: {summary}")
        return summary