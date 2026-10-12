from setuptools import setup, find_packages
from pathlib import Path

BASE_DIR = Path(__file__).parent

def read_file(filename):
    file_path = BASE_DIR / filename
    if file_path.exists():
        return file_path.read_text(encoding="utf-8")
    return ""


def read_requirements():
    """Lê as dependências de runtime da fonte única requirements.txt."""
    requirements_file = BASE_DIR / "requirements.txt"
    return [
        line.strip()
        for line in requirements_file.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]

setup(
    name="pangolin-cli",
    version="2.0.0",
    description="CLI para gerenciamento de experimentos com prompts e LLMs",
    long_description=read_file("README.md"),
    long_description_content_type="text/markdown",

    author="Pangolin contributors",

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

    python_requires=">=3.9",
    install_requires=read_requirements(),

    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
            "black>=23.0",
            "flake8>=6.0",
            "mypy>=1.0",
        ],
        "huggingface": [
            "torch>=2.1",
            "transformers>=4.36",
        ],
        "docs": [
            "sphinx>=5.0",
            "sphinx-rtd-theme>=1.2",
        ],
    },

    entry_points={
        "console_scripts": [
            "pg=pangolin.cli:main",
        ],
    },

    include_package_data=True,

    package_data={
        "pangolin": [
            "config/*.json",
            "config/*.yaml",
            "config/*.yml",
            "schemas/*.yaml",
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
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
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

    zip_safe=False,
)
