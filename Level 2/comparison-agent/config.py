"""
Configuration classes for the meta-agent parameter comparison system.
"""
from dataclasses import dataclass
from typing import Dict, Any, List, Optional
import json
import os.path

try:
    from env_config import get_api_key, get_default_llm_config
    ENV_CONFIG_AVAILABLE = True
except ImportError:
    ENV_CONFIG_AVAILABLE = False


@dataclass
class ParameterOption:
    """Represents a parameter and its possible values."""
    name: str
    description: str
    options: List[Any]
    default: Any = None


@dataclass
class InputExamplePreferences:
    """Preferences for generating input examples."""
    diversity_focus: str = "high"  # low, medium, high
    complexity_level: str = "medium"  # simple, medium, complex
    domain_specific_hints: Optional[List[str]] = None
    edge_cases: bool = True
    custom_instructions: str = ""

    def __post_init__(self):
        if self.domain_specific_hints is None:
            self.domain_specific_hints = []


@dataclass
class WorkflowConfiguration:
    """Main configuration for the meta-agent workflow comparison."""
    # Core workflow information
    task_description: str
    call_example: str
    parameters: List[ParameterOption]

    # Optional preferences
    input_example_preferences: Optional[InputExamplePreferences] = None

    # Execution parameters
    max_examples: int = 5
    timeout_seconds: int = 300
    inconsistency_threshold: float = 0.3  # Threshold for detecting significant differences

    # LLM configuration
    llm_provider: str = "openai"  # openai, or custom
    llm_model: str = "gpt-4"
    llm_api_key: Optional[str] = None
    llm_temperature: Optional[float] = None  # Whether to use temperature in LLM responses

    # Output configuration
    output_file: str = "comparison_results.json"
    verbose: bool = True

    def __post_init__(self):
        if self.input_example_preferences is None:
            self.input_example_preferences = InputExamplePreferences()

        # Auto-load API key from environment if not provided
        if self.llm_api_key is None and ENV_CONFIG_AVAILABLE:
            from env_config import get_api_key
            self.llm_api_key = get_api_key(self.llm_provider)

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "task_description": self.task_description,
            "call_example": self.call_example,
            "parameters": [
                {
                    "name": p.name,
                    "description": p.description,
                    "options": p.options,
                    "default": p.default
                }
                for p in self.parameters
            ],
            "input_example_preferences": {
                "diversity_focus": self.input_example_preferences.diversity_focus if self.input_example_preferences else "high",
                "complexity_level": self.input_example_preferences.complexity_level if self.input_example_preferences else "medium",
                "domain_specific_hints": self.input_example_preferences.domain_specific_hints if self.input_example_preferences else [],
                "edge_cases": self.input_example_preferences.edge_cases if self.input_example_preferences else True,
                "custom_instructions": self.input_example_preferences.custom_instructions if self.input_example_preferences else ""
            },
            "max_examples": self.max_examples,
            "timeout_seconds": self.timeout_seconds,
            "inconsistency_threshold": self.inconsistency_threshold,
            "llm_provider": self.llm_provider,
            "llm_model": self.llm_model,
            "llm_temperature": self.llm_temperature,
            "output_file": self.output_file,
            "verbose": self.verbose
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any], config_dir: str) -> 'WorkflowConfiguration':
        """Create configuration from dictionary."""
        parameters = [
            ParameterOption(
                name=p["name"],
                description=p["description"],
                options=p["options"],
                default=p.get("default")
            )
            for p in data["parameters"]
        ]

        prefs_data = data.get("input_example_preferences", {})
        preferences = InputExamplePreferences(
            diversity_focus=prefs_data.get("diversity_focus", "high"),
            complexity_level=prefs_data.get("complexity_level", "medium"),
            domain_specific_hints=prefs_data.get("domain_specific_hints", []),
            edge_cases=prefs_data.get("edge_cases", True),
            custom_instructions=prefs_data.get("custom_instructions", "")
        )

        # Handle call_example - can be inline code or file path
        call_example = os.path.join(config_dir, data["call_example"])
        if isinstance(call_example, str) and call_example.endswith('.py'):
            # It's a file path, load the content
            if os.path.exists(call_example):
                with open(call_example, 'r') as f:
                    call_example = f.read()
            else:
                raise FileNotFoundError(f"Call example file not found: {call_example}")

        output_file = os.path.join(config_dir, data.get("output_file", "comparison_results.json"))

        return cls(
            task_description=data["task_description"],
            call_example=call_example,
            parameters=parameters,
            input_example_preferences=preferences,
            max_examples=data.get("max_examples", 5),
            timeout_seconds=data.get("timeout_seconds", 300),
            inconsistency_threshold=data.get("inconsistency_threshold", 0.3),
            llm_provider=data.get("llm_provider", "openai"),
            llm_model=data.get("llm_model", "gpt-4"),
            llm_temperature=data.get("llm_temperature", None),
            llm_api_key=data.get("llm_api_key"),
            output_file=output_file,
            verbose=data.get("verbose", True)
        )

    def save_to_file(self, filepath: str):
        """Save configuration to JSON file."""
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load_from_file(cls, filepath: str) -> 'WorkflowConfiguration':
        """Load configuration from JSON file."""
        with open(filepath, 'r') as f:
            data = json.load(f)
        return cls.from_dict(data)
