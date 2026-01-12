from setuptools import setup, find_packages

setup(
    name="synthetic-review-generator",
    version="0.1.0",
    description="LangGraph-based synthetic review generation with quality guardrails",
    author="",
    packages=find_packages(),
    install_requires=[
        "langgraph>=0.2.0",
        "langchain>=0.1.0",
        "langchain-openai>=0.1.0",
        "langchain-community>=0.0.20",
        "pydantic>=2.0.0",
        "pyyaml>=6.0",
        "openai>=1.0.0",
        "ollama>=0.1.0",
        "sentence-transformers>=2.2.0",
        "vaderSentiment>=3.3.2",
        "numpy>=1.24.0",
        "pandas>=2.0.0",
        "typing-extensions>=4.8.0",
    ],
    python_requires=">=3.10",
    entry_points={
        "console_scripts": [
            "review-gen=cli.main:main",
        ],
    },
)

