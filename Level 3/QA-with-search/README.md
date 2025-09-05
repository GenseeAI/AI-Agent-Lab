# QA with Search Agent

An intelligent question-answering agent that combines OpenAI's GPT-4o with real-time internet search capabilities using the Tavily API. The agent automatically determines when search is needed and provides accurate, up-to-date answers with proper source citations.

## Features

- **Smart Search Detection**: Automatically determines if a question requires real-time internet search
- **Intelligent Query Refinement**: Converts user questions into optimized search queries
- **Real-time Information**: Accesses current information from the web using Tavily's advanced search
- **Source Citation**: Provides answers with proper source attribution
- **Fallback Mode**: Answers questions using built-in knowledge when search isn't required
- **Advanced Search Depth**: Uses Tavily's "advanced" search depth for comprehensive results

## Prerequisites

- Python 3.8 or higher
- OpenAI API account with access to GPT-4o
- Tavily API account for web search capabilities
- Internet connection for API calls

## Environment Variables

Create a `.env` file in the project directory with the following variables:

```env
OPENAI_API_KEY=your_openai_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
```

### API Key Setup

1. **OpenAI API Key**: 
   - Sign up at [OpenAI Platform](https://platform.openai.com/)
   - Navigate to API Keys section
   - Create a new API key with GPT-4o access

2. **Tavily API Key**:
   - Sign up at [Tavily](https://tavily.com/)
   - Get your API key from the dashboard
   - Tavily offers free tier with limited searches

## Installation

1. Clone or navigate to the QA-with-search directory:
```bash
cd Simple-Agents/QA-with-search
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables (see Environment Variables section above)

## Usage

### Basic Usage

Run the agent with a predefined question:
```bash
python qa_with_search.py
```

### Interactive Usage

Modify the `main()` function in `qa_with_search.py` to ask different questions:

```python
def main():
    chat_with_search("What is the current weather in New York?")
    # or
    chat_with_search("What are the latest developments in AI?")
```

### Programmatic Usage

Import and use the agent in your own code:

```python
from qa_with_search import chat_with_search

# Ask a question that requires real-time information
response = chat_with_search("What is the current stock price of Apple?")

# Ask a general knowledge question
response = chat_with_search("What is the capital of France?")
```

## Customization

### Model Configuration

You can modify the OpenAI model used by changing the model parameter:

```python
# In the determine_if_search_needed function
response = openai_client.chat.completions.create(
    model="gpt-3.5-turbo",  # Change to different model
    messages=messages,
    max_tokens=200
)
```

### Search Parameters

Customize Tavily search parameters in the `search_internet` function:

```python
def search_internet(query):
    search_results = tavily_client.search(
        query=query, 
        search_depth="basic",  # Change to "basic" or "advanced"
        include_images=True,    # Include images in results
        max_results=5           # Limit number of results
    )
    return search_results
```

### Response Formatting

Modify how search results are formatted in the `generate_response` function:

```python
# Change the number of results used for context
for result in search_results.get('results', [])[:5]:  # Use 5 results instead of 3
    # Customize the context format
    context += f"Source: {title}\nSummary: {content}\nLink: {url}\n\n"
```

### System Prompts

Customize the behavior by modifying system prompts:

```python
# In determine_if_search_needed function
messages = [
    {"role": "system", "content": "You are an expert at determining when questions need real-time information. Respond with 'yes' or 'no' only."},
    # ... rest of the code
]
```

### Error Handling

Add custom error handling for API failures:

```python
def chat_with_search(question):
    try:
        # ... existing code ...
    except Exception as e:
        print(f"Error occurred: {e}")
        return "I apologize, but I encountered an error while processing your question."
```
