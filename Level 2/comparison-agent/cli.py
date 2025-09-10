#!/usr/bin/env python3
"""
Command-line interface for the meta-agent workflow parameter comparison tool.
"""
import argparse
import sys
import json
import os

from config import WorkflowConfiguration
from meta_agent import run_meta_agent

# Load environment variables at startup
try:
    from env_config import setup_environment
    env_status = setup_environment()
except ImportError:
    env_status = {
        "env_file_loaded": False,
        "openai_key_available": False,
        "dotenv_installed": False
    }


def load_config_from_file(config_path: str) -> WorkflowConfiguration:
    """Load configuration from JSON file."""

    config_dir = os.path.dirname(config_path)
    try:
        with open(config_path, 'r') as f:
            config_data = json.load(f)
        return WorkflowConfiguration.from_dict(config_data, config_dir)
    except Exception as e:
        print(f"Error loading configuration from {config_path}: {e}")
        sys.exit(1)


def create_sample_config(output_path: str):
    """Create a sample configuration file."""

    from config import ParameterOption, InputExamplePreferences

    # Create a sample configuration
    parameters = [
        ParameterOption(
            name="tool_override",
            description="Tool override parameter for the API call",
            options=["Tavily:Exa", "Google:Bing", "default"],
            default="default"
        ),
        ParameterOption(
            name="timeout",
            description="Request timeout in seconds",
            options=[30, 60, 120],
            default=30
        )
    ]

    preferences = InputExamplePreferences(
        diversity_focus="high",
        complexity_level="medium",
        domain_specific_hints=["API questions", "search queries", "technical questions"],
        edge_cases=True,
        custom_instructions="Generate diverse questions that would benefit from different tool configurations"
    )

    config = WorkflowConfiguration(
        task_description="Describe what your workflow does here",
        call_example="""
# API Call Example - Replace with your actual workflow
# This example shows how to make an API call with parameter substitution
# You can use Python code, curl commands, or any executable workflow

import requests
import json

# Example 1: Python API call
def make_api_call(question, tool_override="default"):
    url = "https://your-api-endpoint.com/execute"
    payload = {
        "workflow_input": {"question": question},
        "tool_override": tool_override
    }
    response = requests.post(url, json=payload)
    return response.json()

# Example 2: Curl command (comment out Python if using this)
# curl_command = f'''
# curl -X POST https://your-api-endpoint.com/execute \\
#   -H 'Content-Type: application/json' \\
#   -d '{{
#     "workflow_input": {{"question": "{question}"}},
#     "tool_override": "{tool_override}"
#   }}'
# '''
# result = subprocess.run(curl_command, shell=True, capture_output=True, text=True)
# output = result.stdout

# Execute the workflow with parameters
result = make_api_call(question, tool_override=tool_override)
""",
        parameters=parameters,
        input_example_preferences=preferences,
        max_examples=5,
        timeout_seconds=300,
        inconsistency_threshold=0.3,
        llm_provider="openai",
        llm_model="gpt-4",
        llm_api_key="YOUR_API_KEY_HERE",
        output_file="comparison_results.json",
        verbose=True
    )

    try:
        config.save_to_file(output_path)
        print(f"Sample configuration saved to {output_path}")
        print("Please edit the configuration file with your specific workflow details.")
    except Exception as e:
        print(f"Error creating sample configuration: {e}")
        sys.exit(1)


def main():
    """Main CLI function."""

    parser = argparse.ArgumentParser(
        description="Meta-Agent Workflow Parameter Comparison Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --config my_workflow.json
  %(prog)s --create-sample sample_config.json
  %(prog)s --config workflow.json --api-key sk-...
  %(prog)s --config workflow.json --max-examples 10 --timeout 600
        """
    )

    parser.add_argument(
        "--config", "-c",
        type=str,
        help="Path to the workflow configuration JSON file"
    )

    parser.add_argument(
        "--create-sample", "-s",
        type=str,
        metavar="OUTPUT_PATH",
        help="Create a sample configuration file at the specified path"
    )

    parser.add_argument(
        "--api-key",
        type=str,
        help="LLM API key (overrides config file)"
    )

    parser.add_argument(
        "--max-examples",
        type=int,
        help="Maximum number of examples to generate (overrides config)"
    )

    parser.add_argument(
        "--timeout",
        type=int,
        help="Timeout in seconds (overrides config)"
    )

    parser.add_argument(
        "--output", "-o",
        type=str,
        help="Output file path (overrides config)"
    )

    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )

    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Quiet mode - minimal output"
    )

    args = parser.parse_args()

    # Handle sample configuration creation
    if args.create_sample:
        create_sample_config(args.create_sample)
        return

    # Require configuration file for main operation
    if not args.config:
        parser.error("Either --config or --create-sample is required")

    # Load configuration
    config = load_config_from_file(args.config)

    # Apply command-line overrides
    if args.api_key:
        config.llm_api_key = args.api_key

    if args.max_examples:
        config.max_examples = args.max_examples

    if args.timeout:
        config.timeout_seconds = args.timeout

    if args.output:
        config.output_file = args.output

    if args.verbose:
        config.verbose = True

    if args.quiet:
        config.verbose = False

    # Validate API key
    if not config.llm_api_key or config.llm_api_key == "YOUR_API_KEY_HERE":
        print("No API key found in configuration. Checking environment...")

        # Show environment status
        if env_status["env_file_loaded"]:
            print("✓ .env file loaded successfully")
        elif env_status["dotenv_installed"]:
            print("ℹ .env file not found (this is optional)")
        else:
            print("ℹ python-dotenv not installed - install with: pip install python-dotenv")

        # Check for available keys
        if config.llm_provider.lower() == "openai" and env_status["openai_key_available"]:
            print("✓ OpenAI API key found in environment")
        else:
            # Try fallback environment check
            env_key = None
            if config.llm_provider.lower() == "openai":
                env_key = os.getenv("OPENAI_API_KEY")

            if env_key:
                config.llm_api_key = env_key
                print(f"✓ {config.llm_provider.upper()} API key found in environment variables")
            else:
                print(f"Error: No API key found for {config.llm_provider}")
                print(f"Please set {config.llm_provider.upper()}_API_KEY environment variable or use --api-key")
                print("You can also create a .env file with your API key:")
                print(f"  echo '{config.llm_provider.upper()}_API_KEY=your_key_here' > .env")
                sys.exit(1)

    # Run the meta-agent
    try:
        print(f"Starting meta-agent comparison with {config.max_examples} max examples...")
        print(f"Workflow: {config.task_description}")
        print(f"Parameters: {[p.name for p in config.parameters]}")
        print("=" * 60)

        results = run_meta_agent(config)

        print("\\n" + "=" * 60)
        print("COMPARISON COMPLETED")
        print("=" * 60)

        # Print summary
        summary = results["execution_summary"]
        print(f"Total runtime: {summary['total_runtime_seconds']:.1f} seconds")
        print(f"Iterations completed: {summary['total_iterations']}")
        print(f"Significant differences found: {summary['significant_differences_found']}")
        print(f"Average inconsistency score: {summary['average_inconsistency_score']:.3f}")
        print(f"Results saved to: {config.output_file}")

        # Print recommendations
        if results.get("recommendations"):
            print("\\nRecommendations:")
            for rec in results["recommendations"]:
                print(f"  • {rec}")

        # Print most significant finding
        if results.get("most_significant_finding"):
            finding = results["most_significant_finding"]
            print(f"\\nMost significant finding (score: {finding['inconsistency_score']:.3f}):")
            print(f"  {finding['summary']}")

    except KeyboardInterrupt:
        print("\\nOperation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\\nError during comparison: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
