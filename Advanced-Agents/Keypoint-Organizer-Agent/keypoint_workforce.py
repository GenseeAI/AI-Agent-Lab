from __future__ import annotations

import argparse
import os
import sys

from typing import List, Tuple
from datetime import datetime

from camel.agents import ChatAgent
from camel.configs import ChatGPTConfig
from camel.messages import BaseMessage
from camel.models import ModelFactory
from camel.tasks import Task
from camel.toolkits import FunctionTool
from camel.types import ModelPlatformType, ModelType
from camel.societies.workforce import Workforce

from openai import OpenAI
from tavily import TavilyClient

os.environ["TAVILY_API_KEY"] = "dummy key"
os.environ["OPENAI_API_KEY"] = "dummy key"

tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# --- Function tools ---
def tavily_search_internet(query: str):
    """Search the internet using Tavily API."""
    search_results = tavily_client.search(query=query, include_images=False)
    return search_results


# -------------------------
# Prompt templates
# -------------------------
RESEARCH_SYS_TEMPLATE = (
    "You research background knowledge needed to understand a document.\n"
    "Include background ONLY if it would NOT be obvious to a general audience.\n"
    "Perform search if the document references non-obvious concepts or time-sensitive facts.\n"
    "The current time is {current_time}.\n"
    "If any claim may be time-sensitive or uncertain, use the search tools to verify.\n\n"
    "Tools you may call:\n"
    "- tavily_search_internet: perform a web search and extract key points\n\n"
    "Output:\n"
    "Return a tight bullet list of background facts with brief source notes\n"
)


REVIEW_SYS_TEMPLATE = (
    "You verify the organized background facts and context for correctness, freshness, and redundancy.\n"
    "Use the tools to spot-check claims and remove unnecessary or duplicate items.\n"
    "If sources conflict, note the discrepancy and pick the most credible one.\n\n"
    "The current time is {current_time}.\n"
    "If any claim may be time-sensitive or uncertain, use the search tools to verify.\n\n"
    "Tools you may call:\n"
    "- tavily_search_internet: perform a web search and extract key points\n\n"
    "Output:\n"
    "Return the cleaned background list and a short 'Caveats' subsection if needed."
)

SUMMARY_SYS_TEMPLATE = (
    "You turn the reviewed context into a concise briefing that is quick to scan.\n"
    "Keep it fact-based, neutral, and immediately useful.\n\n"
    "Structure:\n"
    "### Background (only non-obvious items)\n"
    "### Key Takeaways\n"
    "### Talking Points\n"
    "### Sources (bullet list of titles + domains)\n"
)

# -------------------------
# Configs
# -------------------------

# Increased from 1024 to prevent truncation

RESEARCH_MODEL_PLATFORM = ModelPlatformType.OPENAI
RESEARCH_MODEL = "gpt-4o"

REVIEW_MODEL_PLATFORM = ModelPlatformType.OPENAI
REVIEW_MODEL = "gpt-4o"

SUMMARY_MODEL_PLATFORM = ModelPlatformType.OPENAI
SUMMARY_MODEL = "gpt-4o-mini"


# -------------------------
# Models
# -------------------------
def build_models() -> Tuple[object, object, object]:
    """
    Create three model backends with consistent configs.
    You can tune these variables if needed.
    """
    research_model = ModelFactory.create(
        model_platform=RESEARCH_MODEL_PLATFORM,
        model_type=RESEARCH_MODEL,
    )
    review_model = ModelFactory.create(
        model_platform=REVIEW_MODEL_PLATFORM,
        model_type=REVIEW_MODEL,
    )
    summary_model = ModelFactory.create(
        model_platform=SUMMARY_MODEL_PLATFORM,
        model_type=SUMMARY_MODEL,
    )
    return research_model, review_model, summary_model

def build_tools() -> List[FunctionTool]:
    return [
        FunctionTool(tavily_search_internet),
    ]

# -------------------------
# Agents & Workforce
# -------------------------

def create_agents(
    tools: List[FunctionTool],
    research_model,
    review_model,
    summary_model,
) -> Tuple[ChatAgent, ChatAgent, ChatAgent]:
    # agent_kwargs = dict(
    #     message_window_size=6,
    #     retry_attempts=3,
    #     retry_delay=1.0,
    #     tool_execution_timeout=30.0,
    #     prune_tool_calls_from_memory=True,
    # )
    research_agent = ChatAgent(
        system_message = BaseMessage.make_assistant_message(
            role_name="Background Researcher",
            content=RESEARCH_SYS_TEMPLATE.format(current_time=datetime.now().date()),
        ),
        model = research_model,
        tools = tools,
        # **agent_kwargs,
    )
    review_agent = ChatAgent(
        system_message = BaseMessage.make_assistant_message(
            role_name="Reviewer",
            content=REVIEW_SYS_TEMPLATE.format(current_time=datetime.now().date()),
        ),
        model = review_model,
        tools = tools,
        # **agent_kwargs,
    )
    summary_agent = ChatAgent(
        system_message = BaseMessage.make_assistant_message(
            role_name="Summary",
            content=SUMMARY_SYS_TEMPLATE,
        ),
        model = summary_model,
        # **agent_kwargs,
    )
    return research_agent, review_agent, summary_agent

def create_workforce(research_agent, review_agent, summary_agent):
    workforce = Workforce("Document Organizer")

    workforce.add_single_agent_worker(
        'Research Specialist, a researcher who does the background research',
        worker = research_agent,
    ).add_single_agent_worker(
        'Result Reviewer, a reviewer who reviews the results and makes sure the information is factually correct',
        worker = review_agent,
    ).add_single_agent_worker(
        'Summarizer, someone who compiles the context into a concise, comprehensive briefing document',
        worker = summary_agent,
    )

    return workforce

# -------------------------
# Helpers
# -------------------------

def extract_final_result(text: str) -> str:
    """
    Robustly extract the last 'Result ---' block (if present).
    Falls back to the full text.
    """
    if not isinstance(text, str):
        return str(text)

    marker = "Result ---"
    last = text.rfind(marker)
    if last == -1:
        # Try a subtask marker
        import re
        m = list(re.finditer(r"---\s*Subtask.*?Result\s*---\s*\n", text, flags=re.IGNORECASE | re.DOTALL))
        if m:
            last = m[-1].end()
        else:
            return text.strip()
    else:
        # Move to the end of the line following 'Result ---'
        nl = text.find("\n", last + len(marker))
        last = nl + 1 if nl != -1 else last + len(marker)

    return text[last:].strip()


# -------------------------
# Runner
# -------------------------
INSTRUCTION = """\
Organize the provided context into a concise, comprehensive briefing suitable for a busy reader.

1) If the document references non-obvious concepts or time-sensitive facts, first research essential background.
2) Review and verify the background; remove duplicates and clearly mark any discrepancies.
3) Produce a clean briefing (Background → Key Takeaways → Talking Points → Sources).

Keep it tight and practical. Avoid fluff.
"""

def run_pipeline(document_context: str) -> str:
    tools = build_tools()
    research_model, review_model, summary_model = build_models()
    research_agent, review_agent, summary_agent = create_agents(tools, research_model, review_model, summary_model)
    workforce = create_workforce(research_agent, review_agent, summary_agent)

    task = Task(
        content=INSTRUCTION,
        additional_info={"document_context": document_context},
        id="0",
    )

    task = workforce.process_task(task)
    return extract_final_result(task.result)


def main():
    document_context = input()
    result = run_pipeline(document_context)
    return result

if __name__ == "__main__":
    main()
    