"""
Setup configuration for SICF Library.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Lê o README para descrição longa
this_directory = Path(__file__).parent
long_description = ""
readme_file = this_directory / "README.md"
if readme_file.exists():
    long_description = readme_file.read_text(encoding='utf-8')

setup(
    name="pangolin",
    version="2.0.0",
    author="Pangolin Team",
    description="Gerenciador de técnicas de prompts",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-repo/pangolin",
    packages=find_packages(exclude=["tests", "docs", "scripts", "data"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Security",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pandas>=2.1.4",
        "openpyxl>=3.1.2",
        "openai>=1.6.1",
        "transformers>=4.36.2",
        "torch>=2.1.2",
        "rouge-score>=0.1.2",
        "huggingface-hub>=0.20.1",
        "psutil>=5.9.7",
        "tqdm>=4.66.1",
        "tiktoken>=0.5.2",
        "numpy>=1.24.4",
        "requests>=2.31.0",
        "tokenizers>=0.15.0",
        "safetensors>=0.4.1",
        "fastuuid>=0.13.0",
        "filelock>=3.18.0",
        "python-dotenv",
        "aiohttp",
        "litellm",
        "pyyaml",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
        "docs": [
            "sphinx>=5.0.0",
            "sphinx-rtd-theme>=1.2.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "pg=pangolin_cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.json", "*.yaml", "*.yml"],
        "config": ["*.json"],
    },
    zip_safe=False,
    keywords="languanges model prompts classification machine-learning nlp pangolin project-manager",
    project_urls={
        "Bug Reports": "https://github.com/your-repo/pangolin/issues",
        "Source": "https://github.com/your-repo/pangolin",
        "Documentation": "https://github.com/your-repo/pangolin#readme",
    },
)
