from .prompt_config import HtpConfig

__all__ = ["HtpConfig"]

    @classmethod
    def from_yaml(cls, yaml_path: str, section: Optional[str] = None) -> "HtpConfig":
        """
        Carrega a configuração de um arquivo YAML.
        Se 'section' for fornecida, navega até essa chave (ex: 'prompt_methodos')
        e extrai os campos dali.
        """
        with open(yaml_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)

        if section:
            if section not in data:
                raise KeyError(f"Seção '{section}' não encontrada no YAML.")
            data = data[section]

        # Validação antes de criar a instância
        cls._validate_yaml_data(data)

        return cls(
            name=data["name"],
            description=data["description"],
            acronimo=data["acronimo"],
            max_iteracao=data["max_iteracao"],
            limite_qualidade=data["limite_qualidade"],
            key_words=data["key_words"],
            prompt_text=data["prompt_text"]
        )

    @staticmethod
    def _validate_yaml_data(data: dict) -> None:
        """Valida se todos os campos obrigatórios estão presentes no dicionário."""
        required_fields = [
            "name", "description", "acronimo",
            "max_iteracao", "limite_qualidade",
            "key_words", "prompt_text"
        ]
        missing = [f for f in required_fields if f not in data]
        if missing:
            raise ValueError(f"Campos obrigatórios ausentes no YAML: {missing}")

        # Validação extra: key_words deve ser um dict com listas
        if not isinstance(data["key_words"], dict):
            raise TypeError("O campo 'key_words' deve ser um dicionário.")
        for cat, words in data["key_words"].items():
            if not isinstance(words, list):
                raise TypeError(f"As palavras da categoria '{cat}' devem ser uma lista.")