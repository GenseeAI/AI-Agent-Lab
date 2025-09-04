# Keypoint Organizer Agent

A sophisticated multi-agent system designed to organize and structure complex documents into concise, actionable briefings. The agent uses a three-stage pipeline: research, review, and summarization, to transform raw document content into well-structured key points suitable for busy readers.

## Features

- **Three-Stage Pipeline**: Research → Review → Summarization workflow
- **Background Research**: Automatic research of non-obvious concepts and time-sensitive facts
- **Fact Verification**: Cross-checking and validation of information accuracy
- **Freshness Detection**: Time-sensitive claim verification using web search
- **Structured Output**: Background → Key Takeaways → Talking Points → Sources format
- **Web Search Integration**: Tavily API for real-time information verification
- **CamelAI Framework**: Built on CamelAI's robust multi-agent architecture
- **Customizable Models**: Different AI models for different stages of processing

## Prerequisites

- Python 3.8 or higher
- OpenAI API account with access to GPT-4o and GPT-4o-mini
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
   - Create a new API key with GPT-4o and GPT-4o-mini access

2. **Tavily API Key**:
   - Sign up at [Tavily](https://tavily.com/)
   - Get your API key from the dashboard
   - Tavily offers free tier with limited searches

## Installation

1. Clone or navigate to the Keypoint-Organizer-Agent directory:
```bash
cd Advanced-Agents/Keypoint-Organizer-Agent
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables (see Environment Variables section above)

## Usage

### Basic Usage

Run the agent with a document context:
```python
from keypoint_workforce import run_pipeline

# Organize a document into key points
document_context = """
The recent developments in quantum computing have shown significant progress in error correction.
IBM's latest quantum processor demonstrates 99.9% fidelity rates, marking a breakthrough in the field.
This advancement could accelerate drug discovery and materials science applications.
"""

result = run_pipeline(document_context)
print(result)
```

### Interactive Usage

Use the main function for interactive input:
```python
from keypoint_workforce import main

# Run interactively
main()
# Then paste your document content when prompted
```

### Programmatic Integration

Use the agent in your own applications:
```python
from keypoint_workforce import run_pipeline

def organize_documents(documents: list) -> list:
    """Process multiple documents efficiently."""
    results = []
    for doc in documents:
        organized = run_pipeline(doc)
        results.append({
            'original': doc,
            'organized': organized
        })
    return results

# Example usage
documents = [
    "Document about AI developments...",
    "Report on climate change impacts...",
    "Analysis of market trends..."
]
organized_docs = organize_documents(documents)
```

### Custom Workflow

Build custom workflows using individual components:
```python
from keypoint_workforce import build_tools, build_models, create_agents, create_workforce

# Create custom pipeline
tools = build_tools()
research_model, review_model, summary_model = build_models()
research_agent, review_agent, summary_agent = create_agents(
    tools, research_model, review_model, summary_model
)
workforce = create_workforce(research_agent, review_agent, summary_agent)

# Process custom task
from camel.tasks import Task
task = Task(
    content="Organize this technical document into key points",
    additional_info={"document_context": "Your document here"},
    id="custom_task"
)
result = workforce.process_task(task)
```

## Customization

### Model Configuration

Change the AI models used for different stages:
```python
# Customize model selection
RESEARCH_MODEL = "gpt-4o"  # Use GPT-4o for research
REVIEW_MODEL = "gpt-4o-mini"  # Use GPT-4o-mini for review
SUMMARY_MODEL = "gpt-3.5-turbo"  # Use GPT-3.5-turbo for summarization

def build_models() -> Tuple[object, object, object]:
    research_model = ModelFactory.create(
        model_platform=ModelPlatformType.OPENAI,
        model_type=RESEARCH_MODEL,
    )
    review_model = ModelFactory.create(
        model_platform=ModelPlatformType.OPENAI,
        model_type=REVIEW_MODEL,
    )
    summary_model = ModelFactory.create(
        model_platform=ModelPlatformType.OPENAI,
        model_type=SUMMARY_MODEL,
    )
    return research_model, review_model, summary_model
```

### Prompt Customization

Modify system prompts for different use cases:
```python
# Custom research prompt
CUSTOM_RESEARCH_TEMPLATE = (
    "You are a specialized research analyst focusing on technical documents.\n"
    "Research background knowledge needed to understand complex technical concepts.\n"
    "Focus on:\n"
    "- Technical terminology and definitions\n"
    "- Industry context and trends\n"
    "- Recent developments and breakthroughs\n"
    "The current time is {current_time}.\n"
    "Always verify time-sensitive claims using search tools.\n\n"
    "Output:\n"
    "Return a structured list of background facts with source citations"
)

# Custom review prompt
CUSTOM_REVIEW_TEMPLATE = (
    "You are a technical reviewer with expertise in multiple domains.\n"
    "Verify the accuracy and relevance of background information.\n"
    "Focus on:\n"
    "- Factual accuracy\n"
    "- Source credibility\n"
    "- Information relevance\n"
    "- Eliminating redundancy\n\n"
    "Output:\n"
    "Return verified information with quality assessments"
)
```

### Agent Configuration

Customize agent behavior and capabilities:
```python
def create_custom_agents(tools, research_model, review_model, summary_model):
    research_agent = ChatAgent(
        system_message=BaseMessage.make_assistant_message(
            role_name="Technical Researcher",
            content=CUSTOM_RESEARCH_TEMPLATE.format(current_time=datetime.now().date()),
        ),
        model=research_model,
        tools=tools,
    )
    
    review_agent = ChatAgent(
        system_message=BaseMessage.make_assistant_message(
            role_name="Technical Reviewer",
            content=CUSTOM_REVIEW_TEMPLATE,
        ),
        model=review_model,
        tools=tools,
    )
    
    summary_agent = ChatAgent(
        system_message=BaseMessage.make_assistant_message(
            role_name="Technical Summarizer",
            content="Create concise technical briefings for expert audiences.",
        ),
        model=summary_model,
    )
    
    return research_agent, review_agent, summary_agent
```

### Search Parameters

Customize web search behavior:
```python
def custom_search_internet(query: str):
    """Custom search with specific parameters."""
    search_results = tavily_client.search(
        query=query, 
        depth="advanced",  # Use advanced search for better results
        include_images=False,
        max_results=5
    )
    return search_results

# Update tools
def build_custom_tools() -> List[FunctionTool]:
    return [FunctionTool(custom_search_internet)]
```

### Output Format

Customize the output structure:
```python
CUSTOM_SUMMARY_TEMPLATE = (
    "You create comprehensive technical briefings.\n\n"
    "Structure:\n"
    "### Executive Summary\n"
    "### Technical Background\n"
    "### Key Findings\n"
    "### Implications\n"
    "### Recommendations\n"
    "### Sources\n"
    "### Appendices (if needed)\n\n"
    "Keep content technical but accessible to the target audience."
)
```

### Error Handling

Add robust error handling:
```python
def robust_pipeline(document_context: str) -> str:
    """Run pipeline with error handling."""
    try:
        return run_pipeline(document_context)
    except Exception as e:
        return f"Error processing document: {str(e)}\n\nOriginal content:\n{document_context}"
```

## Advanced Features

### Custom Tools

Add specialized tools for different domains:
```python
def technical_search_internet(query: str):
    """Specialized search for technical information."""
    # Add technical search logic
    return tavily_client.search(query=query, depth="advanced")

def academic_search_internet(query: str):
    """Search for academic and research papers."""
    # Add academic search logic
    return tavily_client.search(query=query + " academic research paper")

# Add to tools
def build_domain_specific_tools() -> List[FunctionTool]:
    return [
        FunctionTool(technical_search_internet),
        FunctionTool(academic_search_internet)
    ]
```

### Multi-Document Processing

Process multiple related documents:
```python
def process_document_collection(documents: dict) -> dict:
    """Process a collection of related documents."""
    results = {}
    
    for doc_id, content in documents.items():
        # Add context from other documents
        context = f"Related documents: {list(documents.keys())}\n\n{content}"
        result = run_pipeline(context)
        results[doc_id] = result
    
    return results
```

### Quality Assessment

Add quality metrics to the output:
```python
def assess_quality(organized_content: str) -> dict:
    """Assess the quality of organized content."""
    return {
        'completeness': len(organized_content.split()) / 100,  # Simple metric
        'structure': 'Background' in organized_content and 'Key Takeaways' in organized_content,
        'sources': organized_content.count('Source') if 'Source' in organized_content else 0
    }

def enhanced_pipeline(document_context: str) -> dict:
    """Enhanced pipeline with quality assessment."""
    organized = run_pipeline(document_context)
    quality = assess_quality(organized)
    
    return {
        'content': organized,
        'quality_metrics': quality,
        'original_length': len(document_context),
        'organized_length': len(organized)
    }
```

### Caching

Implement result caching for efficiency:
```python
import hashlib
import json
import os

def cached_pipeline(document_context: str, cache_dir: str = "cache") -> str:
    """Run pipeline with caching."""
    # Create cache directory
    os.makedirs(cache_dir, exist_ok=True)
    
    # Generate cache key
    content_hash = hashlib.md5(document_context.encode()).hexdigest()
    cache_file = os.path.join(cache_dir, f"{content_hash}.json")
    
    # Check cache
    if os.path.exists(cache_file):
        with open(cache_file, 'r') as f:
            return json.load(f)['result']
    
    # Run pipeline
    result = run_pipeline(document_context)
    
    # Cache result
    with open(cache_file, 'w') as f:
        json.dump({'result': result}, f)
    
    return result
```
