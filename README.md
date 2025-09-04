## Agent Git Repo

A collection of simple and advanced AI agents. Each agent is self-contained with a clear entrypoint and local dependencies when needed.

### Featured Frameworks
- **Python**: Primary language for all agents
- **Per-agent dependencies**: Declared via local `requirements.txt` files where applicable

### Simple Agents
- **QA-with-search**: Answers questions using a lightweight search/retrieval step.
- **QA-with-translate**: Answers questions with simple translation for multilingual I/O.

### Advanced Agents
- **CodeGen-Agent**: Program synthesis and evaluation workflows (HumanEval tooling and execution pipeline).
- **Finance-Agent**: Multi-step coordination for finance-related tasks (planner/coordinator prompts included).
- **Keypoint-Organizer-Agent**: Orchestrates a workforce-style pipeline to extract and organize key points.
- **Trip-Planner-Agent**: Multi-step itinerary and trip planning with constraints.

### Prerequisites
- **Python**: 3.10+
- **Virtual environment**: `venv` or `conda` (recommended per agent)
- **API keys (if needed)**: Some agents may require external API keys; check agent code/README

### Installation
1) Clone the repository
```bash
git clone https://github.com/your-org/agent-git-repo.git
cd agent-git-repo
```

2) Create and activate a virtual environment (recommended)
```bash
python3 -m venv .venv
source .venv/bin/activate  # macOS/Linux
# On Windows (PowerShell)
# .venv\\Scripts\\Activate.ps1
```

3) Install dependencies per agent (install only what you need)
```bash
# Finance-Agent
echo "Installing Finance-Agent deps"
pip install -r Advanced-Agents/Finance-Agent/requirements.txt

# Keypoint-Organizer-Agent
echo "Installing Keypoint-Organizer-Agent deps"
pip install -r Advanced-Agents/Keypoint-Organizer-Agent/requirements.txt

# Trip-Planner-Agent
echo "Installing Trip-Planner-Agent deps"
pip install -r Advanced-Agents/Trip-Planner-Agent/requirements.txt
```

4) Run an agent
```bash
# Simple agents
python Simple-Agents/QA-with-search/qa_with_search.py
python Simple-Agents/QA-with-translate/QA-with-Trans.py

# Advanced agents (examples)
python Advanced-Agents/Finance-Agent/finance_agent.py
python Advanced-Agents/Trip-Planner-Agent/trip_planner.py
python Advanced-Agents/Keypoint-Organizer-Agent/keypoint_workforce.py
# CodeGen-Agent entrypoints
python Advanced-Agents/CodeGen-Agent/workflow.py
python Advanced-Agents/CodeGen-Agent/humaneval/humaneval.py
```

### Contributing
- **Issues**: Report bugs and request features via issues
- **Branches/PRs**: Use feature branches; open PRs with clear descriptions
- **Style**: Favor clear, readable Python; keep dependencies scoped per agent
- **Docs**: Update this README or add agent-level READMEs for new agents
- **Tests/Examples**: Include minimal tests or usage examples where applicable

Thanks for contributing and exploring these agents!
