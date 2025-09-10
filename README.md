## AI-Agent-Lab: Learn Level 1 to Level 5 AI Agents
![Practical AI Agents](imgs/banner.png)

A collection of simple and advanced AI agents. Each agent is self-contained with a clear entrypoint and local dependencies when needed.

### Levels of AI Agents

#### Level 1: Reactive Agents (Stateless Tools)
- **What they do:** Respond directly to prompts/inputs without memory.
- **Examples:** ChatGPT answers a question, then translates it into another language
- **Why it matters:** Baseline capability — pure input → output.

#### Level 2: Memory-Enhanced Agents (Contextual Helpers)
- **What they do:** Use short-term or long-term memory to improve responses over time.
- **Examples:** LangChain agents with vector databases; AI customer support that remembers past chats.
- **Why it matters:** Moves from "stateless tool" to "personalized assistant."

#### Level 3: Tool-Using Agents (API/Environment Operators)
- **What they do:** Call APIs, browse the web, interact with databases, or control external apps.
- **Examples:** Agents that can use search tools to retrieve time sensitive information
- **Why it matters:** Expands beyond conversation into action-taking.

#### Level 4: Multi-Agent Systems (Collaborative Agents)
- **What they do:** Multiple agents with specialized roles work together.
- **Examples:**
  - One agent researches, another summarizes, another critiques, working together to generate a final plan (Trip planner)
- **Why it matters:** Specialization + collaboration → more robust results.

#### Level 5: Autonomous Task Agents (Goal-Driven Executors)
- **What they do:** Given a goal, they break it into subtasks, plan execution, and complete it with minimal human input.
- **Examples:**
  - Workforce that drafts a plan, assign corresponding workers that have different toolkits, then summarizes the final result
- **Why it matters:** Represents the highest current level of autonomy that's practical and reproducible today.

### Featured Frameworks
- **Python**: Primary language for all agents
- **Per-agent dependencies**: Declared via local `requirements.txt` files where applicable

### Simple Agents
- **QA-with-search**: Answers questions using a lightweight search/retrieval step.
- **QA-with-translate**: Answers questions with simple translation for multilingual I/O.
- **Meta-Agent: Workflow Parameter Comparison**: Generates examples, runs workflow parameter sweeps, and analyzes differences (see `Level 2/comparison-agent/README.md`).

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
