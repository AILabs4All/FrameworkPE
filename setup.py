from setuptools import setup, find_packages
from pathlib import Path

BASE_DIR = Path(__file__).parent

def read_file(filename):
    file_path = BASE_DIR / filename
    if file_path.exists():
        return file_path.read_text(encoding="utf-8")
    return ""

setup(
    name="pangolin-cli",  # 🔥 melhor nome (evita conflito)
    version="2.0.0",
    description="CLI para gerenciamento de experimentos com prompts e LLMs",
    long_description=read_file("README.md"),
    long_description_content_type="text/markdown",

    author="Pangolin Team",
    url="https://github.com/your-repo/pangolin",

    packages=find_packages(
        exclude=[
            "tests", "tests.*",
            "docs", "docs.*",
            "scripts",
            "data",
            "venv",
            "logs",
            "__pycache__"
        ]
    ),

    python_requires=">=3.8",

    install_requires=[
        "pandas>=2.1",
        "openpyxl>=3.1",
        "openai>=1.6",
        "transformers>=4.36",
        "torch>=2.1",
        "rouge-score>=0.1",
        "huggingface-hub>=0.20",
        "psutil>=5.9",
        "tqdm>=4.66",
        "tiktoken>=0.5",
        "numpy>=1.24",
        "requests>=2.31",
        "tokenizers>=0.15",
        "safetensors>=0.4",
        "fastuuid>=0.13",
        "filelock>=3.18",
        "python-dotenv",
        "aiohttp",
        "litellm",
        "pyyaml",
        "typer[all]",   # 🔥 CLI moderno
        "rich"          # 🔥 output bonito
    ],

    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
            "black>=23.0",
            "flake8>=6.0",
            "mypy>=1.0",
        ],
        "docs": [
            "sphinx>=5.0",
            "sphinx-rtd-theme>=1.2",
        ],
    },

    entry_points={
        "console_scripts": [
            "pg=pangolin.cli:main",  # ✅ corrigido
        ],
    },

    include_package_data=True,

    package_data={
        "pangolin": [
            "config/*.json",
            "config/*.yaml",
            "config/*.yml",
        ],
    },

    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Build Tools",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],

    keywords=[
        "llm",
        "prompt-engineering",
        "nlp",
        "machine-learning",
        "cli",
        "experiments",
        "pangolin",
    ],

    project_urls={
        "Bug Reports": "https://github.com/your-repo/pangolin/issues",
        "Source": "https://github.com/your-repo/pangolin",
        "Documentation": "https://github.com/your-repo/pangolin#readme",
    },

    zip_safe=False,
)