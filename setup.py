"""
Setup para Prompt Suite
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="prompt-suite",
    version="0.1.0",
    author="Prompt Suite Team",
    author_email="info@promptsuite.com",
    description="Sistema de gestión de prompts con control de versiones para JSON y YAML",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/promptsuite/prompt-suite",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Markup",
    ],
    python_requires=">=3.8",
    install_requires=[
        "PyYAML>=6.0",
    ],
    extras_require={
        "json": [
            "ujson>=5.0.0",  # Para mejor rendimiento JSON
        ],
        "yaml": [
            "PyYAML>=6.0",  # Ya incluido en install_requires
        ],
        "full": [
            "ujson>=5.0.0",
            "PyYAML>=6.0",
        ],
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
    },
    keywords="prompt management versioning json yaml ai templates",
    project_urls={
        "Bug Reports": "https://github.com/promptsuite/prompt-suite/issues",
        "Source": "https://github.com/promptsuite/prompt-suite",
        "Documentation": "https://promptsuite.readthedocs.io/",
    },
)

