# QA with Translate Agent

A sophisticated question-answering agent that combines question processing with automatic translation capabilities using LangGraph and Anthropic's Claude. The agent follows a two-step workflow: first answering the question, then translating the response to the specified language.

## Features

- **Two-Step Workflow**: First answers questions, then translates responses
- **Multi-Language Support**: Translates to any specified language
- **Honest Responses**: Configured to admit when it doesn't know answers
- **LangGraph Integration**: Uses LangGraph for structured workflow management
- **Claude AI**: Powered by Anthropic's Claude-3-5-Haiku model
- **Streaming Support**: Real-time processing with event streaming
- **Type Safety**: Full TypeScript-style type annotations with TypedDict

## Prerequisites

- Python 3.8 or higher
- Anthropic API account with access to Claude models
- Internet connection for API calls

## Environment Variables

Create a `.env` file in the project directory with the following variable:

```env
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

### API Key Setup

1. **Anthropic API Key**: 
   - Sign up at [Anthropic Console](https://console.anthropic.com/)
   - Navigate to API Keys section
   - Create a new API key
   - Ensure you have access to Claude-3-5-Haiku model

## Installation

1. Clone or navigate to the QA-with-translate directory:
```bash
cd Simple-Agents/QA-with-translate
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables (see Environment Variables section above)

## Usage

### Basic Usage

Import and use the agent in your code:

```python
from QA_with_Trans import app

# Ask a question and get answer in French (default)
response = app("What is the capital of France?")
print(response)

# Ask a question and get answer in Spanish
response = app("What is machine learning?", "Spanish")
print(response)

# Ask a question and get answer in German
response = app("How does photosynthesis work?", "German")
print(response)
```

### Interactive Usage

Create a simple interactive script:

```python
from QA_with_Trans import app

def interactive_qa():
    while True:
        question = input("Enter your question (or 'quit' to exit): ")
        if question.lower() == 'quit':
            break
        
        language = input("Enter target language (default: French): ").strip()
        if not language:
            language = "French"
        
        try:
            response = app(question, language)
            print(f"\nAnswer in {language}: {response}\n")
        except Exception as e:
            print(f"Error: {e}\n")

if __name__ == "__main__":
    interactive_qa()
```

### Programmatic Integration

Use the agent as part of a larger application:

```python
from QA_with_Trans import app

def process_multilingual_questions(questions, languages):
    results = {}
    for question in questions:
        for language in languages:
            key = f"{question}_{language}"
            results[key] = app(question, language)
    return results

# Example usage
questions = ["What is AI?", "How do computers work?"]
languages = ["French", "Spanish", "German"]
results = process_multilingual_questions(questions, languages)
```

## Customization

### Model Configuration

Change the Claude model used by modifying the model parameter:

```python
# In the main script, change the model
llm = ChatAnthropic(model="claude-3-5-sonnet-20241022")  # Use Sonnet instead of Haiku
```

### Language Customization

Modify the default language in the `app` function:

```python
def app(input_question: str, language: str = "Spanish") -> str:  # Change default to Spanish
    # ... rest of the code
```

### Prompt Customization

Customize the prompts used in each step:

```python
def llm_1(state: State) -> State:
    # Customize the question-answering prompt
    prompt = f"Please provide a comprehensive answer to: {state['input_text']}. Be thorough and accurate."
    llm_response = llm.invoke([{"role": "user", "content": prompt}])
    return {"step1_output": llm_response.content}

def llm_2(state: State) -> State:
    # Customize the translation prompt
    prompt = f"Translate the following text to {state['language']} while maintaining the original meaning and tone: {state['step1_output']}"
    llm_response = llm.invoke([{"role": "user", "content": prompt}])
    return {"output_text": llm_response.content}
```

### State Management

Extend the State TypedDict to include additional fields:

```python
class State(TypedDict):
    # Input
    input_text: str
    language: str
    
    # Intermediate
    step1_output: str
    confidence_score: float  # Add confidence scoring
    
    # Output
    output_text: str
    translation_quality: str  # Add translation quality assessment
```

### Graph Customization

Add additional nodes to the workflow:

```python
def build_graph():
    graph_builder = StateGraph(State)
    
    graph_builder.add_node("llm_1", llm_1)
    graph_builder.add_node("llm_2", llm_2)
    graph_builder.add_node("quality_check", quality_check)  # Add quality check node
    
    graph_builder.add_edge(START, "llm_1")
    graph_builder.add_edge("llm_1", "llm_2")
    graph_builder.add_edge("llm_2", "quality_check")
    graph_builder.add_edge("quality_check", END)
    
    graph = graph_builder.compile()
    return graph
```

### Error Handling

Add robust error handling:

```python
def app(input_question: str, language: str = "French") -> str:
    try:
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
        
    except Exception as e:
        return f"Error processing request: {str(e)}"
```

### Streaming Configuration

Modify streaming behavior:

```python
# Change streaming mode
events = graph.stream(state, stream_mode="updates")  # Use "updates" instead of "values"

# Or disable streaming for simpler processing
result = graph.invoke(state)
return result["output_text"]
```
