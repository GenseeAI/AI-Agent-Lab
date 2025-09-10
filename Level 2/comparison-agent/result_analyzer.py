"""
Result analyzer for comparing workflow outputs and detecting inconsistencies.
"""
import json
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from workflow_executor import WorkflowResult
from config import WorkflowConfiguration


@dataclass
class ComparisonResult:
    """Container for comparison analysis results."""
    input_example: Dict[str, Any]
    workflow_results: List[WorkflowResult]
    inconsistency_score: float
    key_differences: List[str]
    consistency_areas: List[str]
    significance_assessment: str
    detailed_analysis: str
    has_significant_differences: bool


class ResultAnalyzer:
    """Analyzes and compares workflow results for factual inconsistencies using LLM."""

    def __init__(self, config: WorkflowConfiguration, llm_interface=None):
        self.config = config
        self.llm_interface = llm_interface
        self.logger = logging.getLogger(__name__)

    def analyze_results(self, workflow_results: List[WorkflowResult]) -> ComparisonResult:
        """Analyze workflow results for factual inconsistencies using LLM."""

        if not workflow_results:
            return self._create_empty_result()

        # Get input example
        input_example = workflow_results[0].input_data

        # Filter successful results
        successful_results = [r for r in workflow_results if r.success]

        if len(successful_results) <= 1:
            return self._create_single_result(input_example, workflow_results)

        # Use LLM to analyze factual inconsistencies
        llm_analysis = self._analyze_with_llm(successful_results, input_example)

        # Extract results from LLM analysis
        inconsistency_score = llm_analysis.get('inconsistency_score', 0.0)
        key_differences = llm_analysis.get('factual_inconsistencies', [])
        consistency_areas = llm_analysis.get('consistent_facts', [])
        significance_assessment = llm_analysis.get('significance_assessment', 'No assessment available')
        detailed_analysis = llm_analysis.get('detailed_analysis', 'No detailed analysis available')

        # Determine if differences are significant
        has_significant_differences = inconsistency_score >= self.config.inconsistency_threshold

        return ComparisonResult(
            input_example=input_example,
            workflow_results=workflow_results,
            inconsistency_score=inconsistency_score,
            key_differences=key_differences,
            consistency_areas=consistency_areas,
            significance_assessment=significance_assessment,
            detailed_analysis=detailed_analysis,
            has_significant_differences=has_significant_differences
        )

    def _analyze_with_llm(self, successful_results: List[WorkflowResult], input_example: Dict[str, Any]) -> Dict[str, Any]:
        """Use LLM to analyze factual inconsistencies between results."""

        if not self.llm_interface:
            self.logger.warning("No LLM interface available, using basic analysis")
            return self._basic_fallback_analysis(successful_results)

        # Prepare results for LLM analysis
        results_for_analysis = []
        for i, result in enumerate(successful_results):
            result_data = {
                'result_id': i + 1,
                'parameters': result.parameters,
                'output': result.output,
                'execution_time': result.execution_time
            }
            results_for_analysis.append(result_data)

        # Build prompt for LLM
        prompt = self._build_factual_analysis_prompt(input_example, results_for_analysis)

        try:
            self.logger.info("Analyzing results with LLM for factual inconsistencies")

            # Use the LLM interface to analyze results
            # We'll use the analyze_differences method but with our custom prompt
            analysis = self._call_llm_for_analysis(prompt)

            self.logger.info(f"LLM analysis completed with inconsistency score: {analysis.get('inconsistency_score', 'N/A')}")
            return analysis

        except Exception as e:
            self.logger.error(f"Error during LLM analysis: {e}")
            return self._basic_fallback_analysis(successful_results)

    def _call_llm_for_analysis(self, prompt: str) -> Dict[str, Any]:
        """Call the LLM with the analysis prompt."""

        if not self.llm_interface:
            self.logger.error("No LLM interface available")
            return {}

        try:
            # Use the OpenAI client directly for custom analysis
            if hasattr(self.llm_interface, 'client') and hasattr(self.llm_interface, 'model'):
                response = self.llm_interface.client.chat.completions.create(
                    model=self.llm_interface.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=self.config.llm_temperature or 0.1  # Low temperature for consistent analysis
                )

                content = response.choices[0].message.content
                self.logger.info(f"LLM response: {content}")

                return self._parse_llm_analysis_response(content)
            else:
                self.logger.error("LLM interface does not have expected client and model attributes")
                return {}

        except Exception as e:
            self.logger.error(f"Error calling LLM: {e}")
            return {}

    def _build_factual_analysis_prompt(self, input_example: Dict[str, Any], results: List[Dict[str, Any]]) -> str:
        """Build prompt for LLM factual inconsistency analysis."""

        prompt = f"""
Task: Analyze the following workflow results for FACTUAL INCONSISTENCIES ONLY.

Your goal is to identify any factual contradictions, incorrect information, or conflicting claims between the different results. Do NOT analyze differences in formatting, presentation style, or subjective opinions.

Input Query/Example:
{json.dumps(input_example, indent=2)}

Workflow Results to Compare:
{json.dumps(results, indent=2, default=str)}

Instructions:
1. Focus ONLY on factual inconsistencies - contradictory facts, incorrect information, or conflicting claims
2. Ignore differences in formatting, presentation style, language tone, or subjective opinions
3. Look for cases where the results make contradictory factual claims about the same topic
4. Consider whether results contradict well-established facts or each other
5. Assess the severity of any factual inconsistencies found

Return your analysis as JSON in this exact format:
{{
    "inconsistency_score": <float between 0.0 and 1.0, where 0.0 = no factual inconsistencies, 1.0 = major factual contradictions>,
    "factual_inconsistencies": [
        "<specific factual inconsistency 1>",
        "<specific factual inconsistency 2>"
    ],
    "consistent_facts": [
        "<factual claim that is consistent across results 1>",
        "<factual claim that is consistent across results 2>"
    ],
    "significance_assessment": "<assessment of how significant the factual inconsistencies are>",
    "detailed_analysis": "<detailed explanation of the factual analysis performed>"
}}

Important: Only flag as inconsistencies if there are actual factual contradictions. Different ways of presenting the same factual information should NOT be considered inconsistencies.
"""
        return prompt

    def _parse_llm_analysis_response(self, content: str) -> Dict[str, Any]:
        """Parse the LLM analysis response."""

        try:
            # Try to extract JSON from the response
            start_idx = content.find('{')
            end_idx = content.rfind('}') + 1
            if start_idx != -1 and end_idx != -1:
                json_str = content[start_idx:end_idx]
                analysis = json.loads(json_str)

                # Validate required fields
                required_fields = ['inconsistency_score', 'factual_inconsistencies', 'consistent_facts',
                                 'significance_assessment', 'detailed_analysis']

                for field in required_fields:
                    if field not in analysis:
                        analysis[field] = [] if field.endswith('ies') or field.endswith('facts') else 'Not provided'

                # Ensure inconsistency_score is a float between 0 and 1
                score = analysis.get('inconsistency_score', 0.0)
                if not isinstance(score, (int, float)):
                    score = 0.0
                analysis['inconsistency_score'] = max(0.0, min(1.0, float(score)))

                return analysis

        except (json.JSONDecodeError, ValueError) as e:
            self.logger.error(f"Failed to parse LLM analysis response: {e}")

        # Return default structure if parsing fails
        return {
            'inconsistency_score': 0.0,
            'factual_inconsistencies': ['Failed to parse LLM response'],
            'consistent_facts': [],
            'significance_assessment': 'Analysis failed - could not parse LLM response',
            'detailed_analysis': 'LLM response could not be parsed correctly'
        }

    def _basic_fallback_analysis(self, successful_results: List[WorkflowResult]) -> Dict[str, Any]:
        """Provide basic fallback analysis when LLM is not available."""

        if len(successful_results) <= 1:
            return {
                'inconsistency_score': 0.0,
                'factual_inconsistencies': [],
                'consistent_facts': ['Single result - no comparison possible'],
                'significance_assessment': 'Only one successful result available',
                'detailed_analysis': 'Cannot analyze factual inconsistencies with fewer than 2 results'
            }

        # Basic comparison - just check if outputs are identical
        outputs = [self._normalize_output(r.output) for r in successful_results]
        unique_outputs = list(set(outputs))

        if len(unique_outputs) == 1:
            return {
                'inconsistency_score': 0.0,
                'factual_inconsistencies': [],
                'consistent_facts': ['All results produced identical outputs'],
                'significance_assessment': 'No inconsistencies detected (identical outputs)',
                'detailed_analysis': 'Basic analysis: All results are identical'
            }
        else:
            return {
                'inconsistency_score': 0.5,  # Medium score for different outputs
                'factual_inconsistencies': [f'Results produced {len(unique_outputs)} different outputs'],
                'consistent_facts': [],
                'significance_assessment': 'Cannot determine factual inconsistencies without LLM analysis',
                'detailed_analysis': f'Basic analysis: Found {len(unique_outputs)} different outputs among {len(successful_results)} results'
            }

    def _normalize_output(self, output: Any) -> str:
        """Normalize output for comparison."""
        if output is None:
            return "None"

        try:
            return json.dumps(output, sort_keys=True, default=str)
        except (TypeError, ValueError):
            return str(output)

    def _create_empty_result(self) -> ComparisonResult:
        """Create an empty comparison result for edge cases."""
        return ComparisonResult(
            input_example={},
            workflow_results=[],
            inconsistency_score=0.0,
            key_differences=[],
            consistency_areas=[],
            significance_assessment="No results to analyze",
            detailed_analysis="Empty result set",
            has_significant_differences=False
        )

    def _create_single_result(self, input_example: Dict[str, Any], workflow_results: List[WorkflowResult]) -> ComparisonResult:
        """Create comparison result for single successful result."""
        successful_count = len([r for r in workflow_results if r.success])

        if successful_count == 0:
            significance = "All executions failed - no factual analysis possible"
            analysis = "No successful results to analyze for factual inconsistencies"
        else:
            significance = "Single successful result - no factual inconsistencies possible"
            analysis = "Only one successful result available - factual consistency analysis requires multiple results"

        return ComparisonResult(
            input_example=input_example,
            workflow_results=workflow_results,
            inconsistency_score=0.0,
            key_differences=[],
            consistency_areas=["Single result - no comparison possible"] if successful_count > 0 else [],
            significance_assessment=significance,
            detailed_analysis=analysis,
            has_significant_differences=False
        )
