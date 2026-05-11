from typing import Dict, Any, List, Tuple
from pathlib import Path
import yaml


class PromptSchemaValidator:
    """Valida arquivos YAML de schemas de técnicas de prompt."""

    REQUIRED_FIELDS = ["technique", "name", "description", "acronym", "strategy", "prompt_text"]
    VALID_STRATEGIES = [
        "direct",
        "zeroshot",
        "free_prompt",
        "progressive_hint",
        "self_hint",
        "progressive_rectification",
        "hypothesis_testing",
    ]

    @classmethod
    def validate(cls, schema_data: Dict[str, Any],
                 schema_path: str = "") -> Tuple[bool, List[str], List[str]]:
        """
        Valida um schema de prompt contra as regras estruturais esperadas.

        Args:
            schema_data: Dicionário carregado do YAML
            schema_path: Caminho do arquivo (para mensagens de erro)

        Returns:
            Tupla (válido, erros, avisos)
        """
        errors = []
        warnings = []

        for field in cls.REQUIRED_FIELDS:
            if field not in schema_data:
                errors.append(f"Campo obrigatório ausente: '{field}'")
            elif not isinstance(schema_data.get(field), str) or not schema_data.get(field).strip():
                errors.append(f"Campo '{field}' deve ser uma string não-vazia")

        strategy = schema_data.get("strategy")

        if strategy and strategy not in cls.VALID_STRATEGIES:
            errors.append(f"Strategy inválida: '{strategy}'. Válidas: {cls.VALID_STRATEGIES}")

        if strategy == "hypothesis_testing":
            if "key_words" not in schema_data:
                errors.append("Estratégia 'hypothesis_testing' requer campo 'key_words'")
            elif not isinstance(schema_data["key_words"], dict):
                errors.append("Campo 'key_words' deve ser um dicionário")

        if strategy in {"progressive_hint", "self_hint", "progressive_rectification"}:
            if "params" not in schema_data:
                errors.append(f"Estratégia '{strategy}' recomenda campo 'params'")

        if "extraction" in schema_data:
            extraction = schema_data["extraction"]
            if isinstance(extraction, dict):
                method = extraction.get("method")
                if method not in {"json", "regex", "template"}:
                    errors.append(
                        f"Método de extraction inválido: '{method}'. Válidos: json, regex, template"
                    )

        prompt_text = schema_data.get("prompt_text", "")
        if prompt_text:
            for placeholder in cls._get_required_placeholders(strategy):
                if f"{{{placeholder}}}" not in prompt_text:
                    errors.append(
                        f"Prompt text não contém placeholder obrigatório: '{placeholder}'"
                    )

        if "categories" not in schema_data:
            warnings.append("Schema sem campo 'categories'")
        if "examples" not in schema_data:
            warnings.append("Schema sem campo 'examples'")
        if "output_format" not in schema_data:
            warnings.append("Schema sem 'output_format' — será usado formato padrão")

        return len(errors) == 0, errors, warnings

    @staticmethod
    def _get_required_placeholders(strategy: str) -> List[str]:
        """Retorna placeholders obrigatórios para cada estratégia."""
        strategy_placeholders = {
            "direct": ["input_framework", "output_format"],
            "zeroshot": ["input_framework", "output_format"],
            "free_prompt": ["input_framework", "output_format"],
            "hypothesis_testing": ["input_framework", "category", "keywords_str"],
            "progressive_hint": ["input_framework", "output_format"],
            "self_hint": ["input_framework", "plan_instructions"],
            "progressive_rectification": ["input_framework"],
        }
        return strategy_placeholders.get(strategy, ["input_framework"])

    @classmethod
    def validate_file(cls, schema_path: str) -> Tuple[bool, List[str], List[str]]:
        """Valida um arquivo YAML de schema."""
        try:
            with open(schema_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)

            if not isinstance(data, dict):
                return False, ["Arquivo YAML não é um dicionário válido"], []

            return cls.validate(data, schema_path)
        except yaml.YAMLError as e:
            return False, [f"Erro ao parsear YAML: {str(e)}"], []
        except Exception as e:
            return False, [f"Erro ao carregar arquivo: {str(e)}"], []

    @classmethod
    def validate_directory(cls, schema_dir: str) -> Dict[str, Tuple[bool, List[str], List[str]]]:
        """Valida todos os arquivos YAML em um diretório."""
        schema_path = Path(schema_dir)
        if not schema_path.exists():
            return {}
        return {
            yaml_file.name: cls.validate_file(str(yaml_file))
            for yaml_file in schema_path.glob("*.yaml")
        }

    @classmethod
    def print_validation_report(
        cls, validation_results: Dict[str, Tuple[bool, List[str], List[str]]]
    ):
        """Imprime relatório legível de validação."""
        print("\n=== Schema Validation Report ===\n")

        total = len(validation_results)
        valid = sum(1 for result in validation_results.values() if result[0])

        print(f"Total de schemas: {total}")
        print(f"Válidos: {valid}")
        print(f"Inválidos: {total - valid}\n")

        for filename, (is_valid, errors, warnings) in validation_results.items():
            status = "✓ VALID" if is_valid else "✗ INVALID"
            print(f"{filename}: {status}")

            if errors:
                print("  Erros:")
                for error in errors:
                    print(f"    - {error}")

            if warnings:
                print("  Avisos:")
                for warning in warnings:
                    print(f"    - {warning}")

            print()
