"""
Workflow executor for running workflows with different parameter configurations.
"""
import time
import logging
from typing import Dict, Any, List
from dataclasses import dataclass
import itertools

from config import WorkflowConfiguration


@dataclass
class WorkflowResult:
    """Container for workflow execution results."""
    input_data: Dict[str, Any]
    parameters: Dict[str, Any]
    output: Any
    execution_time: float
    generated_code: str = ""
    error: str = ""
    success: bool = True


class WorkflowExecutor:
    """Executes workflows with different parameter configurations."""

    def __init__(self, config: WorkflowConfiguration, llm_interface=None):
        self.config = config
        self.llm_interface = llm_interface
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

    def execute_workflow_variations(self, input_example: Dict[str, Any]) -> List[WorkflowResult]:
        """Execute workflow with all parameter combinations for a given input."""

        results = []
        parameter_combinations = self._generate_parameter_combinations()

        self.logger.info(f"Executing {len(parameter_combinations)} parameter combinations")

        for param_combo in parameter_combinations:
            try:
                result = self._execute_single_workflow(input_example, param_combo)
                results.append(result)

            except Exception as e:
                self.logger.error(f"Error executing workflow with parameters {param_combo}: {e}")
                error_result = WorkflowResult(
                    input_data=input_example,
                    parameters=param_combo,
                    output=None,
                    execution_time=0.0,
                    error=str(e),
                    success=False
                )
                results.append(error_result)

        return results

    def _generate_parameter_combinations(self) -> List[Dict[str, Any]]:
        """Generate all combinations of parameter values."""

        param_names = []
        param_values = []

        for param in self.config.parameters:
            param_names.append(param.name)
            param_values.append(param.options)

        combinations = []
        for combo in itertools.product(*param_values):
            param_dict = dict(zip(param_names, combo))
            combinations.append(param_dict)

        return combinations

    def _execute_single_workflow(self, input_data: Dict[str, Any],
                                parameters: Dict[str, Any]) -> WorkflowResult:
        """Execute a single workflow instance with specific parameters."""

        start_time = time.time()

        try:
            # Generate workflow code using LLM if available, otherwise use simple substitution
            if self.llm_interface:
                workflow_code = self.llm_interface.generate_workflow_code(
                    self.config, input_data, parameters
                )
            else:
                workflow_code = self._prepare_workflow_code(input_data, parameters)

            # Execute the workflow code
            local_vars = {}
            global_vars = self._prepare_global_environment()
            self.logger.debug(f"workflow_code: {workflow_code}")
            # self.logger.info(f"global_vars: {global_vars}")

            exec(workflow_code, global_vars, local_vars)

            # Extract the result (assuming the workflow stores result in 'result' variable)
            output = local_vars.get('result', local_vars.get('output', None))
            if output is not None:
                if "response" in output:
                    output = output['response']

            execution_time = time.time() - start_time

            if output is None:
                raise ValueError("Workflow execution did not produce any output")
            return WorkflowResult(
                input_data=input_data,
                parameters=parameters,
                output=output,
                execution_time=execution_time,
                generated_code=workflow_code,
                success=True
            )

        except Exception as e:
            execution_time = time.time() - start_time

            return WorkflowResult(
                input_data=input_data,
                parameters=parameters,
                output=output if 'output' in locals() else None, # type: ignore
                execution_time=execution_time,
                generated_code=workflow_code if 'workflow_code' in locals() else "", # type: ignore
                error=f"{type(e).__name__}: {str(e)}",
                success=False
            )

    def _prepare_workflow_code(self, input_data: Dict[str, Any],
                             parameters: Dict[str, Any]) -> str:
        """Prepare the workflow code with substituted parameters and input."""

        code = self.config.call_example

        # Detect if this is a curl command or shell script
        is_shell_command = any(keyword in code.lower() for keyword in ['curl', 'wget', 'http', 'subprocess'])

        # Handle parameter substitution with more flexible patterns
        for param_name, param_value in parameters.items():
            # Extended patterns for different code types
            patterns = [
                f"{param_name}={param_name}",        # param_name=param_name
                f"{param_name}={{}}",                # param_name={}
                f'"{param_name}"',                   # "param_name"
                f"'{param_name}'",                   # 'param_name'
                f"{{{param_name}}}",                 # {param_name}
                f'"{{{param_name}}}"',               # "{param_name}" (for JSON)
                f"${{{param_name}}}",                # ${param_name} (shell variables)
                f"%%{param_name}%%",                 # %param_name% (Windows batch)
            ]

            # Format the replacement value based on context
            if isinstance(param_value, str):
                if is_shell_command and any(p in code for p in ['"{"', "'{", "'%%"]):
                    # For shell/JSON contexts, escape properly
                    replacement = param_value.replace('"', '"')
                else:
                    replacement = f'"{param_value}"'
            else:
                replacement = str(param_value)

            # Apply replacements
            for pattern in patterns:
                code = code.replace(pattern, replacement)

        # Handle input data substitution
        for key, value in input_data.items():
            patterns = [
                f"{key}={key}",
                f"{key}={{}}",
                f'"{key}"',
                f"'{key}'",
                f"{{{key}}}",
                f'"{{{key}}}"',
                f"${{{key}}}",
                f"%%{key}%%",
            ]

            # Format value based on type and context
            if isinstance(value, str):
                if is_shell_command:
                    replacement = value.replace('"', '"').replace("'", "'")
                else:
                    replacement = f'"{value}"'
            else:
                replacement = str(value)

            for pattern in patterns:
                code = code.replace(pattern, replacement)

        # Add variable assignments at the beginning
        assignments = []

        # Add input data as variables
        for key, value in input_data.items():
            if isinstance(value, str):
                assignments.append(f'{key} = "{value.replace(chr(34), chr(92)+chr(34))}"')  # Escape quotes
            else:
                assignments.append(f'{key} = {value}')

        # Add parameter assignments
        for key, value in parameters.items():
            if isinstance(value, str):
                assignments.append(f'{key} = "{value.replace(chr(34), chr(92)+chr(34))}"')  # Escape quotes
            else:
                assignments.append(f'{key} = {value}')

        # For shell commands, we need different handling
        if is_shell_command:
            # Add subprocess import if needed
            if 'subprocess' in code and 'import subprocess' not in code:
                assignments.insert(0, 'import subprocess')
            if 'requests' in code and 'import requests' not in code:
                assignments.insert(0, 'import requests')
            if 'json' in code and 'import json' not in code:
                assignments.insert(0, 'import json')

        # Combine assignments with the main code
        full_code = '\n'.join(assignments) + '\n\n' + code

        return full_code

    def _prepare_global_environment(self) -> Dict[str, Any]:
        """Prepare the global environment for workflow execution."""

        # Basic imports that workflows might need
        env = {
            '__builtins__': __builtins__,
            'print': print,
            'len': len,
            'str': str,
            'int': int,
            'float': float,
            'list': list,
            'dict': dict,
            'tuple': tuple,
            'set': set,
            'range': range,
            'enumerate': enumerate,
            'zip': zip,
            'sum': sum,
            'max': max,
            'min': min,
            'abs': abs,
            'round': round,
        }

        # Add common libraries if available
        try:
            import json
            env['json'] = json
        except ImportError:
            pass

        try:
            import math
            env['math'] = math
        except ImportError:
            pass

        try:
            import random
            env['random'] = random
        except ImportError:
            pass

        try:
            import re
            env['re'] = re
        except ImportError:
            pass

        return env


class SafeWorkflowExecutor(WorkflowExecutor):
    """Enhanced workflow executor with additional safety checks."""

    def __init__(self, config: WorkflowConfiguration, llm_interface=None, timeout_per_execution: int = 6000):
        super().__init__(config, llm_interface)
        self.timeout_per_execution = timeout_per_execution

    def _execute_single_workflow(self, input_data: Dict[str, Any],
                                parameters: Dict[str, Any]) -> WorkflowResult:
        """Execute workflow with timeout and additional safety checks."""

        import signal

        def timeout_handler(signum, frame):
            raise TimeoutError(f"Workflow execution timed out after {self.timeout_per_execution} seconds")

        start_time = time.time()

        try:
            # Set up timeout
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(self.timeout_per_execution)

            # Execute the workflow
            result = super()._execute_single_workflow(input_data, parameters)

            # Cancel timeout
            signal.alarm(0)

            return result

        except TimeoutError as e:
            execution_time = time.time() - start_time
            return WorkflowResult(
                input_data=input_data,
                parameters=parameters,
                output=None,
                execution_time=execution_time,
                error=str(e),
                success=False
            )
        except Exception as e:
            # Cancel timeout in case of other errors
            signal.alarm(0)
            execution_time = time.time() - start_time

            return WorkflowResult(
                input_data=input_data,
                parameters=parameters,
                output=None,
                execution_time=execution_time,
                error=f"{type(e).__name__}: {str(e)}",
                success=False
            )
        finally:
            # Ensure timeout is always cancelled
            signal.alarm(0)
