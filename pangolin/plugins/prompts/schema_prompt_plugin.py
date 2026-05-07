from .base_prompt import BasePromptPlugin
from plugins.prompts.config import PromptConfigFactory, PromptConfig
from typing import Dict, Any, List, Optional
import pandas as pd
from difflib import SequenceMatcher


class SchemaPromptPlugin(BasePromptPlugin):
    """Plugin genérico que executa técnicas definidas por schemas YAML."""

    def __init__(self, model_plugin: Any, prompt_config: PromptConfig):
        super().__init__(model_plugin, task_config=prompt_config.to_dict())
        self.config = prompt_config

    def execute(self, prompt: str, data_row: pd.Series, columns: List[str], **kwargs) -> List[Dict[str, Any]]:
        incident_text = self.build_input_text(data_row, columns)
        strategy = self.config.strategy
        incident_id = kwargs.get("incident_id")
        execution_fn = getattr(self, f"_execute_{strategy}", None)
        if execution_fn is None:
            raise NotImplementedError(f"Strategy de prompt não implementada: {strategy}")

        return execution_fn(incident_text, data_row, columns, incident_id=incident_id, **kwargs)

    def get_name(self) -> str:
        return self.config.acronym or self.config.technique

    def get_description(self) -> str:
        return self.config.description

    def _render_template(self, template: str, context: Dict[str, Any]) -> str:
        try:
            return template.format(**context)
        except Exception:
            return template

    def _format_prompt(self, context: Dict[str, Any]) -> str:
        prompt_text = self._render_template(self.config.prompt_text, context)
        return prompt_text

    def _calculate_similarity(self, a: str, b: str) -> float:
        if not a or not b:
            return 0.0
        return SequenceMatcher(None, str(a).upper(), str(b).upper()).ratio()

    def _default_output_format(self) -> str:
        return self.config.output_format or "Category: [CAT]\nExplanation: [Reason]"

    def _execute_direct(self, incident_text: str, data_row: pd.Series, columns: List[str], **kwargs) -> List[Dict[str, Any]]:
        context = {
            "input_framework": incident_text,
            "output_format": self._default_output_format(),
            "categories": self._build_categories_text(),
            "examples_section": self._build_examples_text(),
            "context_hints": self._build_context_hints(incident_text)
        }
        prompt_text = self._format_prompt(context)
        response = self.model_plugin.send_prompt(prompt_text, mode=self.config.parameters.get("mode", self.config.strategy), incident_id=kwargs.get("incident_id"))
        processed = self.extract_answer(response)
        return [{
            "Response": response,
            "Processed": processed,
            "Category": processed.get("category", processed.get("Category", "Unknown")),
            "Explanation": processed.get("explanation", processed.get("Explanation", "Unknown"))
        }]

    def _execute_zeroshot(self, incident_text: str, data_row: pd.Series, columns: List[str], **kwargs) -> List[Dict[str, Any]]:
        return self._execute_direct(incident_text, data_row, columns, **kwargs)

    def _execute_free_prompt(self, incident_text: str, data_row: pd.Series, columns: List[str], **kwargs) -> List[Dict[str, Any]]:
        return self._execute_direct(incident_text, data_row, columns, **kwargs)

    def _execute_hypothesis_testing(self, incident_text: str, data_row: pd.Series, columns: List[str], **kwargs) -> List[Dict[str, Any]]:
        key_words = getattr(self.config, "key_words", {})
        max_iter = int(getattr(self.config, "max_iter", 12))
        threshold = float(getattr(self.config, "quality_threshold", 0.9))
        categories = [cat for cat in key_words.keys() if cat.upper() != "UNKNOWN"]

        results: List[Dict[str, Any]] = []
        for i, category in enumerate(categories):
            if i >= max_iter:
                break

            keywords = key_words.get(category, [])
            keywords_str = ", ".join(keywords)
            context = {
                "input_framework": incident_text,
                "category": category,
                "keywords_str": keywords_str,
                "output_format": self._default_output_format()
            }
            prompt_text = self._format_prompt(context)
            response = self.model_plugin.send_prompt(prompt_text, mode=self.config.parameters.get("mode", self.config.strategy), incident_id=kwargs.get("incident_id"))
            extracted = self.extract_answer(response)
            result_cat = extracted.get("category", extracted.get("Category", "UNKNOWN"))
            score = self._calculate_similarity(result_cat, category)
            if score >= threshold:
                results.append({
                    "id": kwargs.get("incident_id"),
                    "informacoes_das_colunas": incident_text,
                    "categoria": result_cat,
                    "explicacao": extracted.get("explanation", extracted.get("Explanation", "")),
                    "categoria_testada": category,
                    "rouge": score,
                    "iteracao": i + 1
                })
                return results

        results.append({
            "id": kwargs.get("incident_id"),
            "informacoes_das_colunas": incident_text,
            "categoria": "UNKNOWN",
            "explicacao": "Nenhuma categoria foi confirmada através do teste de hipóteses",
            "categoria_testada": "ALL",
            "rouge": 0.0,
            "iteracao": max_iter
        })
        return results

    def _execute_progressive_hint(self, incident_text: str, data_row: pd.Series, columns: List[str], **kwargs) -> List[Dict[str, Any]]:
        max_hints = int(getattr(self.config, "max_hints", 4))
        threshold = float(getattr(self.config, "quality_threshold", 0.9))
        hint_template = getattr(self.config, "hint_template", "Hint: The previous prediction was {previous_category}. {input_framework} {output_format}")

        context = {
            "input_framework": incident_text,
            "output_format": self._default_output_format()
        }
        prompt_text = self._format_prompt(context)
        response = self.model_plugin.send_prompt(prompt_text, mode=self.config.parameters.get("mode", self.config.strategy), incident_id=kwargs.get("incident_id"))
        previous_category = self.extract_answer(response).get("category", "Unknown")

        if max_hints == 0:
            extracted = self.extract_answer(response)
            return [{
                "id": kwargs.get("incident_id"),
                "informacoes_das_colunas": incident_text,
                "categoria": extracted.get("category", "Unknown"),
                "explicacao": extracted.get("explanation", "Unknown"),
                "rouge": 0.0,
                "iteracao": 0
            }]

        for i in range(max_hints):
            hint_context = {
                "previous_category": previous_category,
                "input_framework": incident_text,
                "output_format": self._default_output_format()
            }
            hint_prompt = self._render_template(hint_template, hint_context)
            response = self.model_plugin.send_prompt(hint_prompt, mode=self.config.parameters.get("mode", self.config.strategy), incident_id=kwargs.get("incident_id"))
            extracted = self.extract_answer(response)
            current_category = extracted.get("category", "Unknown")
            score = self._calculate_similarity(previous_category, current_category)
            if (i + 1) == max_hints or score >= threshold:
                return [{
                    "id": kwargs.get("incident_id"),
                    "informacoes_das_colunas": incident_text,
                    "categoria": current_category,
                    "explicacao": extracted.get("explanation", "Unknown"),
                    "rouge": score,
                    "iteracao": i + 1
                }]
            previous_category = current_category

        return [{
            "id": kwargs.get("incident_id"),
            "informacoes_das_colunas": incident_text,
            "categoria": previous_category,
            "explicacao": response,
            "rouge": 0.0,
            "iteracao": max_hints
        }]

    def _execute_self_hint(self, incident_text: str, data_row: pd.Series, columns: List[str], **kwargs) -> List[Dict[str, Any]]:
        max_iter = int(getattr(self.config, "max_iter", 4))
        threshold = float(getattr(self.config, "quality_threshold", 0.9))
        plan_instructions = getattr(self.config, "plan_instructions", "Let\'s first understand the problem and devise a plan to solve it step by step.")
        output_format = self._default_output_format()

        initial_prompt = self._render_template(self.config.prompt_text, {
            "input_framework": incident_text,
            "plan_instructions": plan_instructions,
            "output_format": output_format
        })
        self.model_plugin.send_prompt(initial_prompt, mode=self.config.parameters.get("mode", self.config.strategy), incident_id=kwargs.get("incident_id"))
        response = self.model_plugin.send_prompt(initial_prompt, mode=self.config.parameters.get("mode", self.config.strategy), incident_id=kwargs.get("incident_id"))
        previous_category = self.extract_answer(response).get("category", "Unknown")

        for i in range(max_iter):
            refinement_prompt = self._render_template(self.config.prompt_text, {
                "input_framework": incident_text,
                "plan_instructions": plan_instructions,
                "previous_category": previous_category,
                "output_format": output_format
            })
            response = self.model_plugin.send_prompt(refinement_prompt, mode=self.config.parameters.get("mode", self.config.strategy), incident_id=kwargs.get("incident_id"))
            extracted = self.extract_answer(response)
            category = extracted.get("category", "Unknown")
            score = self._calculate_similarity(previous_category, category)
            if (i + 1) == max_iter or score >= threshold:
                return [{
                    "id": kwargs.get("incident_id"),
                    "informacoes_das_colunas": incident_text,
                    "categoria": category,
                    "explicacao": extracted.get("explanation", "Unknown"),
                    "rouge": score,
                    "iteracao": i + 1
                }]
            previous_category = category

        return [{
            "id": kwargs.get("incident_id"),
            "informacoes_das_colunas": incident_text,
            "categoria": previous_category,
            "explicacao": response,
            "rouge": 0.0,
            "iteracao": max_iter
        }]

    def _execute_progressive_rectification(self, incident_text: str, data_row: pd.Series, columns: List[str], **kwargs) -> List[Dict[str, Any]]:
        max_iter = int(getattr(self.config, "max_iter", 4))
        threshold = float(getattr(self.config, "quality_threshold", 0.9))
        masking_template = getattr(self.config, "masking_template", "Replace all occurrences of '{subcategory}' with 'X' in the incident text.")
        rectification_template = getattr(self.config, "rectification_template", "Incident: {input_framework}\nThe answer is probably not: {rejected_category}\nLet\'s think step by step to reclassify.\n{output_format}")

        response = self.model_plugin.send_prompt(self._format_prompt({
            "input_framework": incident_text,
            "output_format": self._default_output_format()
        }), mode=self.config.parameters.get("mode", self.config.strategy), incident_id=kwargs.get("incident_id"))
        current_category = self.extract_answer(response).get("category", "Unknown")
        rejected_categories = []

        for attempt in range(max_iter):
            subcategories = self._get_subcategories(current_category)
            for subcategory in subcategories:
                masked_prompt = self._render_template(masking_template, {
                    "subcategory": subcategory,
                    "input_framework": incident_text
                })
                self.model_plugin.send_prompt(masked_prompt, mode=self.config.parameters.get("mode", self.config.strategy), incident_id=kwargs.get("incident_id"))
                rectified_prompt = self._render_template(rectification_template, {
                    "input_framework": incident_text,
                    "rejected_category": ", ".join(rejected_categories + [current_category]),
                    "output_format": self._default_output_format()
                })
                response = self.model_plugin.send_prompt(rectified_prompt, mode=self.config.parameters.get("mode", self.config.strategy), incident_id=kwargs.get("incident_id"))
                extracted = self.extract_answer(response)
                category = extracted.get("category", "Unknown")
                score = self._calculate_similarity(current_category, category)
                if score >= threshold:
                    return [{
                        "id": kwargs.get("incident_id"),
                        "informacoes_das_colunas": incident_text,
                        "categoria": category,
                        "explicacao": extracted.get("explanation", "Unknown"),
                        "qualidade": score,
                        "iteracao": attempt + 1
                    }]
                rejected_categories.append(current_category)
                current_category = category

        return [{
            "id": kwargs.get("incident_id"),
            "informacoes_das_colunas": incident_text,
            "categoria": current_category,
            "explicacao": response,
            "qualidade": 0.0,
            "iteracao": max_iter
        }]

    def _build_categories_text(self) -> str:
        if not self.config.categories:
            return ""
        return "\n".join([f"- {cat.get('code', '')}: {cat.get('name', '')} - {cat.get('description', '')}" for cat in self.config.categories])

    def _build_examples_text(self) -> str:
        if not self.config.examples or not getattr(self.config, "use_examples", False):
            return ""
        return "\n\n".join([f"Example:\nIncident: {example.get('incident')}\nCategory: {example.get('category')}\nExplanation: {example.get('explanation')}" for example in self.config.examples])

    def _build_context_hints(self, incident_text: str) -> str:
        if not getattr(self.config, "use_context_hints", False):
            return ""
        hints = []
        if any(word in incident_text.lower() for word in ["failed", "login", "brute", "password"]):
            hints.append("• Could be intrusion attempt or account compromise.")
        if any(word in incident_text.lower() for word in ["malware", "virus", "ransomware", "trojan"]):
            hints.append("• Looks like a malware incident.")
        if any(word in incident_text.lower() for word in ["ddos", "dos", "flood", "unavailable"]):
            hints.append("• Consider denial of service attack.")
        if any(word in incident_text.lower() for word in ["data", "leak", "disclosure", "breach"]):
            hints.append("• Investigate potential data leak.")
        if any(word in incident_text.lower() for word in ["exploit", "vulnerability", "cve", "injection"]):
            hints.append("• This may involve vulnerability exploitation.")
        if not hints:
            return ""
        return "ANALYSIS HINTS:\n" + "\n".join(hints)

    def _get_subcategories(self, category: str) -> List[str]:
        if hasattr(self.config, "key_words") and isinstance(getattr(self.config, "key_words"), dict):
            return getattr(self.config, "key_words").get(category, [])
        return []
