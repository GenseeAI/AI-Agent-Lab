from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END
from langchain_anthropic import ChatAnthropic

class State(TypedDict):
    # Input
    input_text: str
    language: str

    # Intermediate
    step1_output: str

    # Output
    output_text: str

llm = ChatAnthropic(model="claude-3-5-haiku-20241022")

def llm_1(state: State) -> State:
    prompt = f"Please answer the following question with your: {state["input_text"]}.  Requirements: you should be honest if you don't know the answer, and please don't guess the solution."
    llm_response = llm.invoke(
        [{"role": "user", "content": prompt}]
    )
    return {"step1_output": llm_response.content}

def llm_2(state: State) -> State:
    prompt = f"Please translate the following text to {state["language"]}: {state["step1_output"]}.  Requirements: you should follow the original text and don't add additional information."
    llm_response = llm.invoke(
        [{"role": "user", "content": prompt}]
    )
    return {"output_text": llm_response.content}


def build_graph():
    graph_builder = StateGraph(State)

    graph_builder.add_node("llm_1", llm_1)
    graph_builder.add_node("llm_2", llm_2)

    graph_builder.add_edge(START, "llm_1")
    graph_builder.add_edge("llm_1", "llm_2")
    graph_builder.add_edge("llm_2", END)
    graph = graph_builder.compile()

    return graph

def app(input_question: str, language: str = "French") -> str:
    state = State(
        input_text=input_question,
        language=language,
    )

    graph = build_graph()

    events = graph.stream(state, stream_mode="values")

    for event in events:
        if "output_text" in event and event["output_text"]:
            return event["output_text"]
    return ""