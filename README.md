# Synthetic Review Data Generator with Quality Guardrails

A LangGraph-based system for generating high-quality synthetic reviews with configurable personas, multi-model support, and comprehensive quality guardrails.

## Features

- **Multi-step Generation Pipeline**: Uses LangGraph to orchestrate review generation with quality validation
- **Quality Guardrails**: Diversity, bias detection, and domain realism validation
- **Multi-Model Support**: OpenAI and Groq integration
- **Configurable Personas**: Define custom personas with specific tones and expectations
- **Real vs Synthetic Comparison**: Compare generated reviews against real review datasets
- **Comprehensive Reporting**: Generate detailed quality reports with metrics

## Installation

```bash
pip install -r requirements.txt
```

## Environment Variables

Create a `.env` file in the project root (or export these in your shell):

```bash
# Required if using OpenAI models (e.g., gpt-4o-mini)
# Get your API key from: https://platform.openai.com/api-keys
OPENAI_API_KEY=your_openai_api_key_here

# Required if using Groq models (e.g., llama-3.3-70b-versatile)
# Get your API key from: https://console.groq.com/keys
GROQ_API_KEY=your_groq_api_key_here
```

**Note**: 
- `OPENAI_API_KEY` is **required** if your configuration uses OpenAI models
- `GROQ_API_KEY` is **required** if your configuration uses Groq models
- Set the appropriate API key(s) based on which provider(s) you use in your config

## Usage

### Generate Reviews

```bash
python -m cli.main generate --config configs/examples/saas_pm_tool.yaml --target-size 300 --output-dir ./output
```

### Compare with Real Reviews

```bash
python -m cli.main compare --synthetic ./output/reviews.json --real ./data/real_reviews.json
```

### Generate Report

```bash
python -m cli.main report --metrics ./output/metrics.json --output ./output/report.md
```

## Configuration

See `configs/examples/saas_pm_tool.yaml` for an example configuration file.

## Project Structure

- `src/`: Core implementation
- `configs/`: Configuration files
- `cli/`: Command-line interface
- `tests/`: Test suite

