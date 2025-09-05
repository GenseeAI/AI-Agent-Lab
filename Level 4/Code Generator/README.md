# Code Generation Agent

An intelligent code generation agent that uses DSPy (Declarative Self-Improving Language Programs) to generate high-quality Python code. The agent follows a two-step reasoning process: first analyzing the incomplete function to understand requirements, then generating the complete implementation based on the guidance.

## Features

- **Two-Step Reasoning Process**: First reasons about the task, then generates code
- **DSPy Integration**: Uses DSPy framework for declarative language model programming
- **HumanEval Dataset Support**: Includes evaluation framework for code generation tasks
- **Structured Output**: Generates code wrapped in XML tags for easy parsing
- **GPT-4o Powered**: Uses OpenAI's GPT-4o model for high-quality code generation
- **Modular Architecture**: Clean separation between reasoning and coding components
- **Evaluation Framework**: Built-in HumanEval evaluation for measuring performance

## Prerequisites

- Python 3.8 or higher
- OpenAI API account with access to GPT-4o
- Internet connection for API calls

## Environment Variables

Create a `.env` file in the project directory with the following variable:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

### API Key Setup

1. **OpenAI API Key**: 
   - Sign up at [OpenAI Platform](https://platform.openai.com/)
   - Navigate to API Keys section
   - Create a new API key with GPT-4o access

## Installation

1. Clone or navigate to the CodeGen-Agent directory:
```bash
cd Advanced-Agents/CodeGen-Agent
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables (see Environment Variables section above)

## Usage

### Basic Usage

Run the agent with a predefined task:
```python
from workflow import codegen_workflow

# Example incomplete function
task = """
def truncate_number(number: float) -> float:
    \"\"\" Given a positive floating point number, it can be decomposed into
    and integer part (largest integer smaller than given number) and decimals
    (leftover part always smaller than 1).

    Return the decimal part of the number.
    >>> truncate_number(3.5)
    0.5
    \"\"\"
"""

result = codegen_workflow(task)
print(result)
```

### Interactive Usage

Modify the main function in `workflow.py`:

```python
if __name__ == "__main__":
    task = """
def fibonacci(n: int) -> int:
    \"\"\"Calculate the nth Fibonacci number.
    >>> fibonacci(5)
    5
    >>> fibonacci(10)
    55
    \"\"\"
"""
    result = codegen_workflow(task)
    print("Generated code:")
    print(result)
```

### Programmatic Integration

Use the agent in your own applications:

```python
from workflow import CodeGen

# Create a custom instance
codegen = CodeGen()

# Generate code for multiple tasks
tasks = [
    "def reverse_string(s: str) -> str:\n    \"\"\"Reverse a string.\"\"\"",
    "def is_palindrome(s: str) -> bool:\n    \"\"\"Check if string is palindrome.\"\"\""
]

for task in tasks:
    result = codegen.forward(task)
    print(f"Task: {task}")
    print(f"Result: {result}\n")
```

## Customization

### Model Configuration

Change the OpenAI model used by modifying the model parameter:

```python
# In workflow.py, change the model
model = dspy.LM('gpt-3.5-turbo', max_tokens=1000)  # Use different model
```

### Reasoning Prompts

Customize the reasoning prompt in the `Reasoning` class:

```python
class Reasoning(dspy.Signature):
    """You are an expert at providing guidance for a coding task.
    
    Given an incomplete python function with its docstring. 
    Analyze the requirements step by step and provide clear implementation guidance.
    Focus on edge cases and potential pitfalls.
    """
    incomplete_function: str = dspy.InputField()
    guidance: str = dspy.OutputField()
```

### Coding Prompts

Modify the coding prompt in the `Coding` class:

```python
class Coding(dspy.Signature):
    """You are an expert at coding.
    
    Your task is to complete the given python function by using the information 
    from its docstring and provided tips. Ensure the code is efficient and handles edge cases.
    """
    incomplete_function: str = dspy.InputField()
    guidance: str = dspy.InputField()
    function_body: str = dspy.OutputField(
        desc="Only the function body should be returned, and wrapped in <result> and </result> tags. Include proper error handling and edge cases."
    )
```

### Output Format

Customize the output format by modifying the `function_body` description:

```python
function_body: str = dspy.OutputField(
    desc="Return only the function body with proper indentation. Include docstring if needed."
)
```

### Error Handling

Add custom error handling:

```python
def codegen_workflow(task):
    try:
        result = workflow(task=task)
        return result
    except Exception as e:
        print(f"Error generating code: {e}")
        return f"Error: {str(e)}"
```

### Token Limits

Adjust token limits for different use cases:

```python
# For longer functions
model = dspy.LM('gpt-4o', max_tokens=2000)

# For shorter functions
model = dspy.LM('gpt-4o', max_tokens=500)
```

## Evaluation

### HumanEval Integration

The agent includes HumanEval evaluation framework:

```python
from humaneval.humaneval import HumanEvalDataset

# Load the dataset
dataset = HumanEvalDataset()

# Evaluate generated code
for i in range(len(dataset)):
    problem = dataset[i]
    completion = codegen_workflow(problem)
    result = dataset.evaluate(i, completion)
    print(f"Problem {i}: {result}")
```

### Performance Metrics

Track performance using built-in evaluation:

```python
def evaluate_performance():
    dataset = HumanEvalDataset()
    results = []
    
    for i in range(min(10, len(dataset))):  # Test first 10 problems
        problem = dataset[i]
        completion = codegen_workflow(problem)
        result = dataset.evaluate(i, completion)
        results.append(result)
    
    # Calculate pass@k metrics
    overall_result = dataset.overall_evaluate(
        sample_file="results.jsonl",
        k=[1, 10, 100],
        n_workers=4,
        timeout=3.0
    )
    return overall_result
```
