````markdown
# Meta-Agent: Workflow Parameter Comparison

A meta-agent that generates diverse input examples, runs a workflow under many parameter configurations, and analyzes outputs for factual inconsistencies and parameter impact using an LLM.

This repository provides a CLI and library components to: (1) generate test inputs, (2) execute your workflow across parameter combinations, and (3) analyze differences to surface parameters that materially change the results.

## Features

- Generate diverse input examples tailored to expose parameter-driven differences
- Run workflows with all combinations of configured parameters (safe execution environment)
- Use an LLM (OpenAI) to generate inputs, synthesize executable workflow code, and analyze factual inconsistencies
- Produce a JSON report with execution summary, parameter impact analysis, and recommendations
- CLI for local runs and a programmable API for integrating into other pipelines

## Repository layout

- `cli.py` — Command-line entrypoint for running comparisons and creating sample configs
- `config.py` — `WorkflowConfiguration`, `ParameterOption`, and helpers for reading/writing JSON configs
- `env_config.py` — (optional) helpers to load environment API keys (if present)
- `llm_interface.py` — LLM abstraction and OpenAI adapter used for example/code/analysis generation
- `meta_agent.py` — Orchestrates example generation, execution, and analysis (MetaAgent)
- `workflow_executor.py` — Executes workflows for each parameter combination (safe executor included)
- `result_analyzer.py` — Compares outputs and identifies factual inconsistencies
- `configs/example_config/` — Example configs and a sample workflow call example
- `requirements.txt` — Python dependencies

## Prerequisites

- Python 3.8 or higher
- An OpenAI API key if you plan to use the OpenAI LLM integration
- Internet connection for LLM/API calls

## Environment variables

Create a `.env` file in the project root or set environment variables directly. The common variable used by the project is:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

If you provide credentials via CLI (`--api-key`) they will override environment values.

## Installation

1. Create a virtual environment (recommended):

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Quick start — Create a sample configuration

The project includes code to generate a sample JSON config you can edit. From the repository root run:

```bash
python cli.py --create-sample configs/sample_workflow_config.json
```

Edit the generated file to point `call_example` at your workflow (either inline Python/curl snippet or a path to a `.py` file inside the same folder).

## Running a comparison (CLI)

Basic usage with a prepared configuration file:

```bash
python cli.py --config path/to/your_workflow.json
```

Override the API key, output file, or tuning parameters from the CLI:

```bash
python cli.py --config my_workflow.json --api-key sk-... --max-examples 10 --timeout 600 --output results.json
```

The CLI prints a concise summary and saves a detailed JSON report to the configured `output_file`.

## Programmatic usage

You can import the components directly from Python:

```python
from config import WorkflowConfiguration
from meta_agent import run_meta_agent

config = WorkflowConfiguration.load_from_file('configs/my_workflow.json')
results = run_meta_agent(config)
print(results['execution_summary'])
```

Note: the CLI imports `run_meta_agent` from `meta_agent.py` — the same function is available for programmatic integration.

## Configuration reference

Configurations are JSON files that map to the `WorkflowConfiguration` dataclass in `config.py`. Key fields:

- `task_description` (string): Short description of the workflow under test
- `call_example` (string): Either an inline code snippet or a relative path to a `.py` file that performs the workflow call
- `parameters` (array): List of parameter objects with `name`, `description`, `options`, and optional `default`
- `input_example_preferences` (object): Hints for how the LLM should generate input examples
- `max_examples` (int): How many input examples / iterations to run
- `timeout_seconds` (int): Total timeout for the run
- `inconsistency_threshold` (float): Score threshold to mark differences as significant
- `llm_provider`, `llm_model`, `llm_api_key`, `llm_temperature` — LLM settings
- `output_file` (string): Path to write JSON results
- `verbose` (bool): Enable verbose logging

Example parameter entry:

```json
{
  "name": "tool_override",
  "description": "Which search/tool provider to use",
  "options": ["Tavily:Exa", "Google:Bing", "default"],
  "default": "default"
}
```

The `call_example` can be a template that uses placeholder names matching parameter names and input fields; the executor will attempt smart substitutions or the LLM can generate executable code for you.

## How it works (high level)

1. Meta-agent requests an LLM to generate a challenging input example based on `task_description`, `parameters`, and `input_example_preferences`.
2. The `WorkflowExecutor` runs the workflow under every combination of `parameters` defined in the config. A safe executor with timeouts is available.
3. `ResultAnalyzer` compares outputs. If an LLM is available it performs factual inconsistency detection; otherwise a fallback basic comparison runs.
4. The final JSON report contains execution statistics, parameter impact analysis, significant findings, and recommendations.

## Customization

- Change the LLM model/provider by editing `llm_provider` and `llm_model` in your config or by passing `--api-key` on the CLI.
- Edit `call_example` to provide your own code/curl snippet or point to a `.py` script. If you prefer the LLM to synthesize runnable code, leave a template and let the LLM generate.
- Tune `input_example_preferences` to bias the LLM generation toward diversity, domain hints, or edge cases.

## Error handling & troubleshooting

- If you see OpenAI import errors, ensure `openai` is installed and `OPENAI_API_KEY` is set.
- If no API key is found, the CLI prints steps to set an environment variable or use `--api-key`.
- Execution failures for specific parameter combinations are recorded in the JSON report; the CLI prints per-iteration failure summaries.

## Example run (full)

```bash
# create and edit sample config
python cli.py --create-sample configs/sample_workflow_config.json
# edit the config file to set your API key or use --api-key
python cli.py --config configs/sample_workflow_config.json --api-key sk-... --max-examples 3
```

## Contributing

Contributions welcome. Open a PR with focused changes (docs, tests, bugfixes). If you add features that change config semantics, update this README and `configs/example_config` accordingly.
