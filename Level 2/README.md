## Level 2: Memory-Enhanced Agents (Contextual Helpers)

Level 2 agents extend simple reactive tools by keeping and using context. They use short-term or long-term memory to provide more helpful, personalized, or stateful responses across interactions.

### What this level's agents do
- Store and recall recent conversation context or user state
- Use context to improve answer relevance and follow-up behavior
- Combine simple tool calls with remembered facts for consistent multi-step interactions

### Provided agent(s) in this level
- `Meta-Agent: Workflow Parameter Comparison` — orchestrates example generation, runs workflows across parameter combinations, and analyzes factual inconsistencies. See the agent README: `README.md`.

### Getting started
- Read the level definition and goals in `README-overall.md` for the full Level 2 description and rationale.
- Open the agent README (`README.md`) for installation, configuration, and CLI usage. It contains instructions to create a sample config and run the meta-agent.

### Quick start (example)
1. Create a Python venv and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Create a sample configuration and run a short comparison:

```bash
python cli.py --create-sample configs/sample_workflow_config.json
# Edit the config file to point at your workflow and set API keys (or use --api-key)
python cli.py --config configs/sample_workflow_config.json --max-examples 3
```

For details on configuration fields, LLM settings, and analysis outputs, consult `README.md` and `config.py`.
