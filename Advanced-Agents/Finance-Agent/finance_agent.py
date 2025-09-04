import json
import os
from datetime import datetime
from typing import Any, Dict, List

# CamelAI imports
from camel.toolkits.function_tool import FunctionTool
from camel.agents import ChatAgent
from camel.messages import BaseMessage
from camel.toolkits import MathToolkit
from camel.models import ModelFactory
from camel.societies.workforce import Workforce
from camel.tasks import Task

# Local imports
from utils import extract_final_result
from snapshot_manager import SnapshotManager, Snapshot

from tavily import TavilyClient
from openai import OpenAI
import os



# os.environ["TAVILY_API_KEY"] = "dummy key"
# os.environ["OPENAI_API_KEY"] = "dummy key"

tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def tavily_search_internet(query: str):
    """Search the internet using Tavily API."""
    search_results = tavily_client.search(query=query, depth="advanced", include_images=False)
    return search_results

def multi_agent_workforce(input_question: str, tool_fn) -> dict:
    """
    Orchestrates Coordinator + Planner + Workers. Wraps the search tool to create snapshots.
    Adds a freshness-aware verification pass and injects the current date to prompts.
    """
    # Date injection
    cur_date = datetime.now().date().isoformat()

    # Build workers
    search_tools = [FunctionTool(tool_fn)]
    search_agent = ChatAgent(
        system_message=BaseMessage.make_assistant_message(
            role_name="Data Collector",
            content=(f"""
You are a data collector agent.\n
You are given a question and collect relevant data from the internet.\n
Return the results in text format.\n
You have access to the following tool:\n- {tool_fn.__name__}: {getattr(tool_fn, '__doc__', '')}\n
Today's date: {cur_date}
- If the user question includes keywords like "current", "recent", "now", "today" or other cues for recency:
- Treat the answer as time-sensitive and prefer sources fetched within the last 90 days.
- If only older sources exist, explicitly **highlight** this limitation.
- If newer sources contradict older ones, treat the older data as **incorrect**.
- Always record the date considered "today" in the final answer."""
            ),
        ),
        model=ModelFactory.create(model_platform="openai", model_type="gpt-4o-mini"),
        tools=search_tools,
    )

    math_tools = MathToolkit().get_tools()
    math_agent = ChatAgent(
        system_message=BaseMessage.make_assistant_message(
            role_name="Math Agent",
            content=(
                "You are a math agent.\n"
                "You are given a question and you need to answer it using the tools provided."
            ),
        ),
        model=ModelFactory.create(model_platform="openai", model_type="gpt-4o-mini"),
        tools=math_tools,
    )

    writer_agent = ChatAgent(
        system_message=BaseMessage.make_assistant_message(
            role_name="Writer", 
            content="""
You are the Writer Agent.
Your job is to construct the final answer from the provided evidence and the question
Today's date: {cur_date}
- If the user question includes keywords like "current", "recent", "now", "today" or other cues for recency:
- Treat the answer as time-sensitive and prefer sources fetched within the last 90 days.
- If only older sources exist, explicitly **highlight** this limitation.
- If newer sources contradict older ones, treat the older data as **incorrect**.
- Always record the date considered "today" in the final answer.
            """
        ),
        model=ModelFactory.create(model_platform="openai", model_type="gpt-4o-mini"),
    )
    # Read prompts and append recency policy
    with open("prompts/Coordinator_System_Prompt.md", "r", encoding="utf-8") as f:
        coordinator_system_prompt = f.read() + "\n"
    with open("prompts/Task_Planner_System_Prompt.md", "r", encoding="utf-8") as f:
        task_planner_system_prompt = f.read() + "\n"

    coordinator = ChatAgent(
        system_message=BaseMessage.make_assistant_message(
            role_name="Coordinator", content=coordinator_system_prompt
        ),
        model=ModelFactory.create(model_platform="openai", model_type="gpt-4o-mini"),
    )
    planner = ChatAgent(
        system_message=BaseMessage.make_assistant_message(
            role_name="Task Planner", content=task_planner_system_prompt
        ),
        model=ModelFactory.create(model_platform="openai", model_type="gpt-4o-mini"),
    )


    workforce = Workforce(
        "Deep Research Agent",
        coordinator_agent=coordinator,
        task_agent=planner,
        share_memory=False,
    )

    workforce.add_single_agent_worker(
        description="worker agent for web search, returns the contents of the page of search results",
        worker=search_agent,
    ).add_single_agent_worker(
        description="worker agent for math calculations",
        worker=math_agent,
    ).add_single_agent_worker(
        description="worker agent for writing the final answer",
        worker=writer_agent,
    )

    # Setup snapshot management
    snapshot_dir = os.environ.get("SNAPSHOT_DIR", "snapshots")
    snapshot_mgr = SnapshotManager(snapshot_dir)
    all_snapshots: List[Snapshot] = []

    def tool_with_snapshots(query: str) -> Dict[str, Any]:
        """Wrapper that adds snapshotting to the search tool."""
        raw = tool_fn(query)
        if isinstance(raw, dict) and "results" in raw:
            results = raw.get("results", [])
        elif isinstance(raw, list):
            results = raw
        else:
            results = []

        # Normalize results to have URL field
        norm: List[Dict[str, Any]] = []
        for item in results:
            if isinstance(item, dict) and "url" in item:
                norm.append(item)
            elif isinstance(item, str) and item.startswith("http"):
                norm.append({"url": item})

        # Create snapshots for all URLs
        snaps: List[Snapshot] = []
        for r in norm:
            url = r.get("url")
            if not url:
                continue
            snap = snapshot_mgr.snapshot_url(url)
            if snap:
                r["snapshot_meta"] = {
                    "url": snap.url,
                    "fetched_at": snap.fetched_at,
                    "content_path": snap.content_path,
                    "content_hash": snap.content_hash,
                }
                snaps.append(snap)

        all_snapshots.extend(snaps)
        return {"results": norm, "snapshots": [
            {
                "url": s.url,
                "fetched_at": s.fetched_at,
                "content_path": s.content_path,
                "content_hash": s.content_hash,
            } for s in snaps
        ]}

    # Replace the search tool with our snapshot-enabled version
    def _proxy_tool(query: str) -> Dict[str, Any]:
        """Proxy search tool that also creates Crawl4AI snapshots."""
        return tool_with_snapshots(query)

    # Rebind the search tool at runtime
    search_agent.tools = [FunctionTool(_proxy_tool)]

    # Process task
    task = Task(content=input_question, id="0")
    processed_task = workforce.process_task(task)

    # Extract final result using the provided function
    final_result = extract_final_result(processed_task.result)

    return {
        "content": processed_task.content,
        "state": processed_task.state,
        "result": final_result,
        "cur_date": cur_date,
    }


def app(input_question: str, tool_fn=None) -> dict:
    """Main application entry point."""
    return multi_agent_workforce(input_question, tool_fn)


def main() -> None:
    tool_fn = tavily_search_internet
    input_question = input()
    result = app(input_question, tool_fn)
    print(result)
    return result # Return just the result content like keypoint_workforce.py


if __name__ == "__main__":
    main()