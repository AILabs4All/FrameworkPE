"""Implementação de modelo usando HuggingFace Transformers."""

from __future__ import annotations

from typing import Any, Dict, Optional

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

from .base_model import BaseModel


class HuggingfaceModel(BaseModel):
    """Modelo para execução usando HuggingFace Transformers."""

    def __init__(self, config: Dict[str, Any]):
        self.tokenizer: Optional[AutoTokenizer] = None
        self.model: Optional[AutoModelForCausalLM] = None
        self.device: str = "cuda" if torch.cuda.is_available() else "cpu"
        super().__init__(config)

    def setup_model(self) -> None:
        """Configura o modelo e tokenizer do HuggingFace."""
        try:
            model_path = self.config.get("model_path", self.model_name)
            if not model_path:
                raise ValueError("Nome do modelo ou caminho não especificado")

            # Configurar dispositivo
            self.device = self._get_device()
            
            # Configurações de loading
            load_config = self.config.get("load_config", {})
            
            self.logger.info("Carregando tokenizer: %s", model_path)
            self.tokenizer = AutoTokenizer.from_pretrained(
                model_path,
                **load_config.get("tokenizer", {})
            )
            
            self.logger.info("Carregando modelo: %s (dispositivo: %s)", model_path, self.device)
            self.model = AutoModelForCausalLM.from_pretrained(
                model_path,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                device_map="auto" if self.device == "cuda" else None,
                **load_config.get("model", {})
            )
            
            if self.device == "cpu":
                self.model = self.model.to(self.device)
                
            self.logger.info("Modelo HuggingFace configurado com sucesso")
            
        except Exception as exc:
            self.logger.error("Erro ao configurar modelo HuggingFace: %s", exc)
            raise

    def send_prompt(self, prompt: str, **kwargs: Any) -> str:
        """Envia prompt para o modelo e retorna a resposta."""
        if self.tokenizer is None or self.model is None:
            raise RuntimeError("Modelo não foi configurado corretamente")
            
        mode = kwargs.get("mode", "default")
        
        try:
            self._apply_rate_limit(kwargs.get("rate_limit", 0.0))
            input_tokens = self.count_tokens(prompt)
            
            # Tokenizar entrada
            inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
            
            # Configurações de geração
            generation_config = self._build_generation_config(kwargs)
            
            # Gerar resposta
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs["input_ids"],
                    **generation_config
                )
            
            # Decodificar e processar resposta
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            content = response.replace(prompt, "").strip()
            
            output_tokens = self.count_tokens(content)
            self._log_interaction(prompt, content, input_tokens, output_tokens, mode, kwargs.get('incident_id'))
            
            return content
            
        except Exception as exc:
            self.logger.error("Erro ao processar prompt: %s", exc)
            return f"Erro ao executar modelo HuggingFace: {exc}"

    def _get_device(self) -> str:
        """Determina o dispositivo a ser usado."""
        device_config = self.config.get("device", "auto")
        
        if device_config == "auto":
            return "cuda" if torch.cuda.is_available() else "cpu"
        elif device_config == "cuda" and not torch.cuda.is_available():
            self.logger.warning("CUDA solicitado mas não disponível, usando CPU")
            return "cpu"
        else:
            return device_config

    def _build_generation_config(self, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Constrói configuração para geração de texto."""
        config = {
            "max_new_tokens": kwargs.get("max_new_tokens", kwargs.get("max_tokens", self.max_tokens)),
            "do_sample": kwargs.get("do_sample", True),
            "temperature": kwargs.get("temperature", self.temperature),
            "top_p": kwargs.get("top_p", 0.9),
            "top_k": kwargs.get("top_k", 50),
            "pad_token_id": self.tokenizer.eos_token_id,
        }
        
        # Remover valores None
        return {k: v for k, v in config.items() if v is not None}

    def get_model_info(self) -> Dict[str, Any]:
        """Retorna informações do modelo incluindo configurações específicas."""
        base_info = super().get_model_info()
        base_info.update({
            "device": self.device,
            "torch_available": torch.cuda.is_available() if hasattr(torch, 'cuda') else False,
            "model_loaded": self.model is not None,
            "tokenizer_loaded": self.tokenizer is not None,
        })
        return base_info