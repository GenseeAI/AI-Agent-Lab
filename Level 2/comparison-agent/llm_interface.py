"""
LLM interface for generating input examples and analysis.
"""
import json
import logging
import sys
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod

try:
    import openai
except ImportError:
    openai = None

from config import WorkflowConfiguration


class LLMInterface(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    def generate_input_examples(self, config: WorkflowConfiguration,
                                existing_examples: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
        """Generate input examples for testing workflow variations."""
        pass

    @abstractmethod
    def analyze_differences(self, results: List[Dict[str, Any]],
                          config: WorkflowConfiguration) -> Dict[str, Any]:
        """Analyze differences between workflow results."""
        pass

    @abstractmethod
    def generate_workflow_code(self, config: WorkflowConfiguration,
                             input_data: Dict[str, Any],
                             parameters: Dict[str, Any]) -> str:
        """Generate actual executable workflow code based on the call example."""
        pass


class OpenAILLM(LLMInterface):
    """OpenAI GPT interface for example generation and analysis."""

    def __init__(self, api_key: Optional[str], model: str = "gpt-4"):
        if openai is None:
            raise ImportError("OpenAI package not installed. Install with: pip install openai")

        self.client = openai.OpenAI(api_key=api_key)
        self.model = model
        self.logger = self._setup_logger()

    def _setup_logger(self) -> logging.Logger:
        """Setup logger for LLM interface."""
        logger = logging.getLogger(__name__)

        # Set level to INFO to show detailed logging
        logger.setLevel(logging.INFO)

        # Only add handler if none exists to avoid duplicate logs
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    def generate_input_examples(self, config: WorkflowConfiguration,
                                existing_examples: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
        """Generate input examples using OpenAI."""

        prompt = self._build_example_generation_prompt(config, existing_examples)
        self.logger.debug(f"Prompt: {prompt}")

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=config.llm_temperature or 0.7
            )

            content = response.choices[0].message.content
            self.logger.debug(f"Response: {content}")
            if not content:
                raise ValueError("OpenAI returned empty response for input examples")
            examples = self._parse_examples_from_response(content)
            self.logger.debug(f"examples: {examples}")

            self.logger.info(f"Generated {len(examples)} input examples")
            return examples

        except Exception as e:
            self.logger.error(f"OpenAI API error: {e}")
            print("\nError: Failed to generate input examples using OpenAI API")
            print(f"Details: {e}")
            print("Please check your API key and try again.")
            sys.exit(1)

    def analyze_differences(self, results: List[Dict[str, Any]],
                            config: WorkflowConfiguration) -> Dict[str, Any]:
        """Analyze differences between results using OpenAI."""

        prompt = self._build_analysis_prompt(results, config)
        self.logger.debug(f"Prompt: {prompt}")

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=config.llm_temperature or 0.3
            )

            content = response.choices[0].message.content
            self.logger.debug(f"Response: {content}")
            if not content:
                raise ValueError("OpenAI returned empty response for analysis")
            analysis = self._parse_analysis_from_response(content)
            self.logger.info(f"Analysis: {analysis}")

            return analysis

        except Exception as e:
            self.logger.error(f"OpenAI API error: {e}")
            print("\nError: Failed to analyze differences using OpenAI API")
            print(f"Details: {e}")
            print("Please check your API key and try again.")
            sys.exit(1)

    def generate_workflow_code(self, config: WorkflowConfiguration,
                             input_data: Dict[str, Any],
                             parameters: Dict[str, Any]) -> str:
        """Generate actual executable workflow code based on the call example."""

        prompt = self._build_code_generation_prompt(config, input_data, parameters)
        self.logger.debug(f"Prompt: {prompt}")

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=config.llm_temperature or 0.1  # Lower temperature for more consistent code generation
            )

            content = response.choices[0].message.content
            self.logger.debug(f"Response: {content}")
            if not content:
                raise ValueError("OpenAI returned empty response for workflow code generation")
            generated_code = self._extract_code_from_response(content)
            self.logger.info(f"Generated workflow code: {generated_code}")

            self.logger.info("Generated workflow code using OpenAI")
            return generated_code

        except Exception as e:
            self.logger.error(f"OpenAI API error: {e}")
            print("\nError: Failed to generate workflow code using OpenAI API")
            print(f"Details: {e}")
            print("Please check your API key and try again.")
            sys.exit(1)

    def _build_code_generation_prompt(self, config: WorkflowConfiguration,
                                    input_data: Dict[str, Any],
                                    parameters: Dict[str, Any]) -> str:
        """Build prompt for generating workflow code."""

        prompt = f"""
Task: Generate executable Python code based on the provided call example template.

Workflow Description: {config.task_description}

Call Example Template:
{config.call_example}

Input Data: {json.dumps(input_data, indent=2)}
Parameters: {json.dumps(parameters, indent=2)}

Instructions:
1. Take the call example as a template
2. Replace ALL placeholder values with the actual input data and parameters provided
3. Generate complete, executable Python code
4. The code should be ready to run without modification
5. Ensure all variable substitutions are made correctly
6. The final result should be stored in a variable called 'result'

Return ONLY the executable Python code, no explanations or markdown formatting.
"""
        return prompt

    def _extract_code_from_response(self, content: str) -> str:
        """Extract Python code from the LLM response."""

        # Remove code block markers if present
        lines = content.strip().split('\n')

        # Remove leading/trailing markdown code block markers
        if lines and lines[0].strip().startswith('```'):
            lines = lines[1:]
        if lines and lines[-1].strip().startswith('```'):
            lines = lines[:-1]

        # Remove any language identifiers
        if lines and lines[0].strip() in ['python', 'py']:
            lines = lines[1:]

        return '\n'.join(lines).strip()

    def _build_example_generation_prompt(self, config: WorkflowConfiguration,
                                         existing_examples: Optional[List[Dict[str, Any]]] = None) -> str:
        """Build prompt for generating input examples."""

        prefs = config.input_example_preferences

        prompt = f"""
Task: Generate diverse input examples for testing a workflow with different parameter configurations.
Your goal is to generate test examples that have the highest chance of showing inconsistencies among the same workflow that calls different LLM models or toolings (for example, search provided by Tavily or Exa).

Workflow Description: {config.task_description}

Call Example:
{config.call_example}

Parameters to test:
{json.dumps([{"name": p.name, "description": p.description, "options": p.options} for p in config.parameters], indent=2)}

"""
        if prefs.domain_specific_hints:
            prompt += f"""
Generation Preferences:
- Domain Hints: {', '.join(prefs.domain_specific_hints) if prefs and prefs.domain_specific_hints else 'None'}
"""

        if existing_examples:
            prompt += f"\n\nHere are the existing examples and their comparison results.  Please use them to avoid duplications and also generate examples that can demonstrate new differences:\n{json.dumps(existing_examples, indent=2)}"

        prompt += f"""

Requirements:
1. The example should be specific and easy for to see the inconsistencies (for example, the answer is a number or a few words), rather than an open question.
2. The example should have enough complexities (which may involve analyze a document and aggregate results from multiple sources), not straightforward answers that can be easily answered by LLMs or a direct answer from the search engine.
3. Learn from existing examples (especially examples that have shown differences in the past) to increase question complexities.
4. Try generating diverse examples from different domains or areas, given existing examples.
3. Generate 1 diverse input example.  Put the example that is most likely to show the difference at the top.
4. Return examples as a JSON array in the format: {{"examples": [{{"description": <description>, "input": <input>}}, ...]}}

Each example should contain the input fields that the workflow expects (e.g., 'question' for Q&A workflows).
"""

        return prompt

    def _build_analysis_prompt(self, results: List[Dict[str, Any]], config: WorkflowConfiguration) -> str:
        """Build prompt for analyzing workflow result differences."""

        prompt = f"""
Task: Analyze differences between workflow results to identify parameter impact.

Workflow: {config.task_description}

Results to analyze:
{json.dumps(results, indent=2, default=str)}

Analysis Requirements:
1. Calculate an inconsistency score (0.0 = identical, 1.0 = completely different)
2. Identify key differences between parameter configurations
3. Note which parameters seem to have the most impact
4. Provide significance assessment of findings

Return analysis as JSON:
{{
    "inconsistency_score": <float between 0.0 and 1.0>,
    "key_differences": [<list of key differences found>],
    "consistency_areas": [<list of areas where results were consistent>],
    "parameter_impact": {{
        "<parameter_name>": {{
            "impact_level": "<high/medium/low>",
            "description": "<description of impact>"
        }}
    }},
    "significance_assessment": "<assessment of overall significance>",
    "recommendations": [<list of recommendations>]
}}
"""
        return prompt

    def _parse_examples_from_response(self, content: str) -> List[Dict[str, Any]]:
        """Parse examples from LLM response."""
        try:
            # Try to extract JSON from the response
            start_idx = content.find('[')
            end_idx = content.rfind(']') + 1
            if start_idx != -1 and end_idx != -1:
                json_str = content[start_idx:end_idx]
                data = json.loads(json_str)
                return data
        except json.JSONDecodeError:
            pass

        # Exit if parsing fails - no fallback for OpenAI errors
        self.logger.error("Failed to parse examples from OpenAI response")
        print("\nError: OpenAI returned invalid response format")
        print("The response could not be parsed as JSON.")
        sys.exit(1)

    def _parse_analysis_from_response(self, content: str) -> Dict[str, Any]:
        """Parse analysis from LLM response."""
        try:
            # Try to extract JSON from the response
            start_idx = content.find('{')
            end_idx = content.rfind('}') + 1
            if start_idx != -1 and end_idx != -1:
                json_str = content[start_idx:end_idx]
                return json.loads(json_str)
        except json.JSONDecodeError:
            pass

        # Exit if parsing fails - no fallback for OpenAI errors
        self.logger.error("Failed to parse analysis from OpenAI response")
        print("\nError: OpenAI returned invalid response format")
        print("The analysis response could not be parsed as JSON.")
        sys.exit(1)

def create_llm_interface(provider: str, api_key: Optional[str], model: str) -> LLMInterface:
    """Factory function to create the appropriate LLM interface."""

    if provider.lower() == "openai":
        return OpenAILLM(api_key, model)
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")
