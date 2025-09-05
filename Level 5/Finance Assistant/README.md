# Finance Agent

A sophisticated multi-agent financial research system that combines web search, mathematical calculations, and intelligent coordination to provide comprehensive financial analysis. The agent uses CamelAI's workforce architecture with specialized agents for data collection, mathematical analysis, and report writing, enhanced with snapshot management for data verification.

## Features

- **Multi-Agent Workforce**: Coordinator, Task Planner, and specialized worker agents
- **Web Search Integration**: Advanced internet search using Tavily API
- **Mathematical Analysis**: Built-in mathematical calculation capabilities
- **Snapshot Management**: Automatic web page snapshots for data verification
- **Time-Sensitive Analysis**: Freshness-aware verification for current financial data
- **Stock Data Integration**: Real-time stock price and historical data access
- **Structured Output**: Comprehensive financial reports with source attribution
- **CamelAI Framework**: Built on CamelAI's robust multi-agent architecture

## Prerequisites

- Python 3.8 or higher
- OpenAI API account with access to GPT-4o-mini
- Tavily API account for web search capabilities
- Internet connection for API calls

## Environment Variables

Create a `.env` file in the project directory with the following variables:

```env
OPENAI_API_KEY=your_openai_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
SNAPSHOT_DIR=snapshots  # Optional: custom snapshot directory
```

### API Key Setup

1. **OpenAI API Key**: 
   - Sign up at [OpenAI Platform](https://platform.openai.com/)
   - Navigate to API Keys section
   - Create a new API key with GPT-4o-mini access

2. **Tavily API Key**:
   - Sign up at [Tavily](https://tavily.com/)
   - Get your API key from the dashboard
   - Tavily offers free tier with limited searches

## Installation

1. Clone or navigate to the Finance-Agent directory:
```bash
cd Advanced-Agents/Finance-Agent
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables (see Environment Variables section above)

## Usage

### Basic Usage

Run the agent with a financial question:
```python
from finance_agent import app

# Ask about current market conditions
result = app("What is the current status of the S&P 500 and what are the main factors affecting it?")
print(result['result'])
```

### Interactive Usage

Use the main function for interactive input:
```python
from finance_agent import main

# Run interactively
main()
# Then type your question when prompted
```

### Programmatic Integration

Use the agent in your own applications:
```python
from finance_agent import multi_agent_workforce, tavily_search_internet

# Custom workflow
def custom_financial_analysis(question: str):
    result = multi_agent_workforce(question, tavily_search_internet)
    return {
        'answer': result['result'],
        'sources': result.get('snapshots', []),
        'date': result['cur_date']
    }

# Example usage
analysis = custom_financial_analysis("What are the current trends in renewable energy stocks?")
```

### Stock Data Analysis

Access real-time stock information:
```python
from stock_utils import get_current_stock_price, get_historical_stock_data

# Get current price
price = get_current_stock_price("AAPL")
print(f"Apple stock price: {price}")

# Get historical data
history = get_historical_stock_data("AAPL", "6mo")
print(f"6-month history: {history}")
```

## Customization

### Agent Configuration

Modify agent roles and capabilities:
```python
# Customize Data Collector agent
search_agent = ChatAgent(
    system_message=BaseMessage.make_assistant_message(
        role_name="Financial Data Collector",
        content="""
You are a specialized financial data collector.
Focus on:
- Market data and trends
- Company financials
- Economic indicators
- Regulatory news
Always verify data freshness and source credibility.
        """
    ),
    model=ModelFactory.create(model_platform="openai", model_type="gpt-4o-mini"),
    tools=search_tools,
)
```

### Model Selection

Change the AI models used by different agents:
```python
# Use different models for different tasks
coordinator_model = ModelFactory.create(model_platform="openai", model_type="gpt-4o")
planner_model = ModelFactory.create(model_platform="openai", model_type="gpt-4o-mini")
worker_model = ModelFactory.create(model_platform="openai", model_type="gpt-3.5-turbo")
```

### Search Parameters

Customize web search behavior:
```python
def custom_search_internet(query: str):
    """Custom search with specific parameters."""
    search_results = tavily_client.search(
        query=query, 
        depth="basic",  # Change to "basic" or "advanced"
        include_images=True,
        max_results=10
    )
    return search_results
```

### Snapshot Management

Configure snapshot behavior:
```python
# Custom snapshot directory
snapshot_mgr = SnapshotManager("custom_snapshots")

# Custom snapshot settings
def custom_snapshot_tool(query: str):
    raw = tavily_search_internet(query)
    # Add custom snapshot logic
    return raw
```

### Workforce Architecture

Add custom agents to the workforce:
```python
# Add a technical analysis agent
technical_agent = ChatAgent(
    system_message=BaseMessage.make_assistant_message(
        role_name="Technical Analyst",
        content="You analyze technical indicators and chart patterns."
    ),
    model=ModelFactory.create(model_platform="openai", model_type="gpt-4o-mini"),
    tools=technical_tools,
)

workforce.add_single_agent_worker(
    description="Technical analysis specialist",
    worker=technical_agent,
)
```

### Prompt Customization

Modify system prompts for different use cases:
```python
# Custom coordinator prompt
coordinator_prompt = """
You are a financial research coordinator.
Specialize in:
- Market analysis
- Risk assessment
- Investment recommendations
- Economic forecasting

Coordinate research efforts to provide comprehensive financial insights.
"""

coordinator = ChatAgent(
    system_message=BaseMessage.make_assistant_message(
        role_name="Financial Coordinator", 
        content=coordinator_prompt
    ),
    model=ModelFactory.create(model_platform="openai", model_type="gpt-4o-mini"),
)
```

### Error Handling

Add robust error handling:
```python
def robust_financial_analysis(question: str):
    try:
        result = multi_agent_workforce(question, tavily_search_internet)
        return result
    except Exception as e:
        return {
            'error': str(e),
            'content': 'Unable to complete analysis',
            'result': 'Analysis failed due to technical issues'
        }
```

## Advanced Features

### Custom Tools

Add specialized financial tools:
```python
def calculate_risk_metrics(ticker: str) -> dict:
    """Calculate various risk metrics for a stock."""
    # Implementation for risk calculations
    return {
        'beta': 1.2,
        'sharpe_ratio': 0.85,
        'volatility': 0.15
    }

# Add to workforce
risk_tools = [FunctionTool(calculate_risk_metrics)]
risk_agent = ChatAgent(
    system_message=BaseMessage.make_assistant_message(
        role_name="Risk Analyst",
        content="You analyze investment risk and return metrics."
    ),
    model=ModelFactory.create(model_platform="openai", model_type="gpt-4o-mini"),
    tools=risk_tools,
)
```

### Data Verification

Implement custom verification logic:
```python
def verify_financial_data(data: dict) -> dict:
    """Verify the accuracy of financial data."""
    verification_issues = []
    
    # Check data freshness
    if data.get('date'):
        days_old = _days_between(data['date'], datetime.now().isoformat())
        if days_old > 30:
            verification_issues.append({
                'severity': 'highlight',
                'message': f'Data is {days_old} days old'
            })
    
    return {
        'data': data,
        'verification_issues': verification_issues
    }
```
