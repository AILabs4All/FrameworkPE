import json
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional


@dataclass
class PromptConfig:
    technique: str
    name: str
    description: str
    acronym: str
    strategy: str
    prompt_text: str
    input_builder: Optional[str] = None
    extraction: Dict[str, Any] = field(default_factory=lambda: {
        "method": "json",
        "unknown_category": "UNKNOWN"
    })
    output_format: Optional[str] = None
    categories: List[Dict[str, Any]] = field(default_factory=list)
    examples: List[Dict[str, Any]] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    templates: Dict[str, str] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        cls._validate_required_fields(data)
        default_extraction = {
            "method": "json",
            "unknown_category": "UNKNOWN"
        }
        return cls(
            technique=data["technique"],
            name=data["name"],
            description=data["description"],
            acronym=data["acronym"],
            strategy=data["strategy"],
            prompt_text=data["prompt_text"],
            input_builder=data.get("input_builder"),
            extraction=data.get("extraction", default_extraction),
            output_format=data.get("output_format"),
            categories=data.get("categories", []),
            examples=data.get("examples", []),
            parameters=data.get("params", data.get("parameters", {})),
            metadata=data.get("metadata", {}),
            templates=data.get("templates", {}),
        )

    @staticmethod
    def _validate_required_fields(data: Dict[str, Any]):
        required_fields = [
            "technique",
            "name",
            "description",
            "acronym",
            "strategy",
            "prompt_text"
        ]
        missing = [field for field in required_fields if field not in data]
        if missing:
            raise ValueError(f"Campos obrigatórios ausentes no schema: {missing}")

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class HtpConfig(PromptConfig):
    key_words: Dict[str, List[str]] = field(default_factory=dict)
    max_iter: int = 12
    quality_threshold: float = 0.9

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        base = PromptConfig.from_dict(data)
        return cls(
            technique=base.technique,
            name=base.name,
            description=base.description,
            acronym=base.acronym,
            strategy=base.strategy,
            prompt_text=base.prompt_text,
            input_builder=base.input_builder,
            extraction=base.extraction,
            output_format=base.output_format,
            categories=base.categories,
            examples=base.examples,
            parameters=base.parameters,
            metadata=base.metadata,
            templates=base.templates,
            key_words=data.get("key_words", {}),
            max_iter=int(data.get("params", {}).get("max_iter", data.get("max_iter", 12))),
            quality_threshold=float(data.get("params", {}).get("quality_threshold", data.get("quality_threshold", 0.9)))
        )

    @staticmethod
    def validate(config: "HtpConfig"):
        if not isinstance(config.key_words, dict):
            raise TypeError("O campo 'key_words' deve ser um dicionário no schema HTP")


@dataclass
class ProgressiveHintConfig(PromptConfig):
    max_hints: int = 4
    quality_threshold: float = 0.9
    hint_template: str = ""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        base = PromptConfig.from_dict(data)
        return cls(
            technique=base.technique,
            name=base.name,
            description=base.description,
            acronym=base.acronym,
            strategy=base.strategy,
            prompt_text=base.prompt_text,
            input_builder=base.input_builder,
            extraction=base.extraction,
            output_format=base.output_format,
            categories=base.categories,
            examples=base.examples,
            parameters=base.parameters,
            metadata=base.metadata,
            templates=base.templates,
            max_hints=int(data.get("params", {}).get("max_hints", data.get("max_hints", 4))),
            quality_threshold=float(data.get("params", {}).get("quality_threshold", data.get("quality_threshold", 0.9))),
            hint_template=data.get("hint_template", data.get("templates", {}).get("hint_template", ""))
        )


@dataclass
class SelfHintConfig(PromptConfig):
    max_iter: int = 4
    quality_threshold: float = 0.9
    plan_instructions: str = ""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        base = PromptConfig.from_dict(data)
        return cls(
            technique=base.technique,
            name=base.name,
            description=base.description,
            acronym=base.acronym,
            strategy=base.strategy,
            prompt_text=base.prompt_text,
            input_builder=base.input_builder,
            extraction=base.extraction,
            output_format=base.output_format,
            categories=base.categories,
            examples=base.examples,
            parameters=base.parameters,
            metadata=base.metadata,
            templates=base.templates,
            max_iter=int(data.get("params", {}).get("max_iter", data.get("max_iter", 4))),
            quality_threshold=float(data.get("params", {}).get("quality_threshold", data.get("quality_threshold", 0.9))),
            plan_instructions=data.get("plan_instructions", data.get("templates", {}).get("plan_instructions", ""))
        )


@dataclass
class ProgressiveRectificationConfig(PromptConfig):
    max_iter: int = 4
    quality_threshold: float = 0.9
    masking_template: str = ""
    rectification_template: str = ""
    key_words: Dict[str, List[str]] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        base = PromptConfig.from_dict(data)
        return cls(
            technique=base.technique,
            name=base.name,
            description=base.description,
            acronym=base.acronym,
            strategy=base.strategy,
            prompt_text=base.prompt_text,
            input_builder=base.input_builder,
            extraction=base.extraction,
            output_format=base.output_format,
            categories=base.categories,
            examples=base.examples,
            parameters=base.parameters,
            metadata=base.metadata,
            templates=base.templates,
            max_iter=int(data.get("params", {}).get("max_iter", data.get("max_iter", 4))),
            quality_threshold=float(data.get("params", {}).get("quality_threshold", data.get("quality_threshold", 0.9))),
            masking_template=data.get("masking_template", data.get("templates", {}).get("masking_template", "")),
            rectification_template=data.get("rectification_template", data.get("templates", {}).get("rectification_template", "")),
            key_words=data.get("key_words", {})
        )


@dataclass
class FreePromptConfig(PromptConfig):
    use_examples: bool = True
    use_structured_output: bool = True
    use_context_hints: bool = False
    temperature_override: Optional[float] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        base = PromptConfig.from_dict(data)
        return cls(
            technique=base.technique,
            name=base.name,
            description=base.description,
            acronym=base.acronym,
            strategy=base.strategy,
            prompt_text=base.prompt_text,
            input_builder=base.input_builder,
            extraction=base.extraction,
            output_format=base.output_format,
            categories=base.categories,
            examples=base.examples,
            parameters=base.parameters,
            metadata=base.metadata,
            templates=base.templates,
            use_examples=bool(data.get("params", {}).get("use_examples", data.get("use_examples", True))),
            use_structured_output=bool(data.get("params", {}).get("use_structured_output", data.get("use_structured_output", True))),
            use_context_hints=bool(data.get("params", {}).get("use_context_hints", data.get("use_context_hints", False))),
            temperature_override=data.get("params", {}).get("temperature_override", data.get("temperature_override"))
        )


@dataclass
class ZeroShotConfig(PromptConfig):
    system_prompt: str = ""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        base = PromptConfig.from_dict(data)
        return cls(
            technique=base.technique,
            name=base.name,
            description=base.description,
            acronym=base.acronym,
            strategy=base.strategy,
            prompt_text=base.prompt_text,
            input_builder=base.input_builder,
            extraction=base.extraction,
            output_format=base.output_format,
            categories=base.categories,
            examples=base.examples,
            parameters=base.parameters,
            metadata=base.metadata,
            templates=base.templates,
            system_prompt=data.get("system_prompt", data.get("templates", {}).get("system_prompt", ""))
        )


class PromptConfigFactory:
    registry: Dict[str, Any] = {
        "hypothesis_testing": HtpConfig,
        "htp": HtpConfig,
        "progressive_hint": ProgressiveHintConfig,
        "self_hint": SelfHintConfig,
        "progressive_rectification": ProgressiveRectificationConfig,
        "free_prompt": FreePromptConfig,
        "zeroshot": ZeroShotConfig
    }

    @classmethod
    def create(cls, data: Dict[str, Any]) -> PromptConfig:
        strategy = data.get("strategy") or data.get("technique")
        if not strategy:
            raise ValueError("O schema deve informar o campo 'strategy' ou 'technique'")

        config_class = cls.registry.get(strategy)
        if config_class is None:
            raise ValueError(f"Strategy desconhecida no schema: {strategy}")

        return config_class.from_dict(data)
