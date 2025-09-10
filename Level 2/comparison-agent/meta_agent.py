"""
Main meta-agent for workflow parameter comparison.
"""
import json
import time
import logging
from typing import List, Dict, Any
from dataclasses import asdict

from config import WorkflowConfiguration
from llm_interface import create_llm_interface, LLMInterface
from workflow_executor import WorkflowExecutor, SafeWorkflowExecutor
from result_analyzer import ResultAnalyzer, ComparisonResult


class MetaAgent:
    """Meta-agent for automated workflow parameter comparison."""

    def __init__(self, config: WorkflowConfiguration):
        self.config = config
        self.logger = self._setup_logging()

        # Initialize components
        self.llm = self._create_llm_interface()
        self.executor = self._create_executor()
        self.analyzer = ResultAnalyzer(config, self.llm)

        # State tracking
        self.generated_examples = []
        self.comparison_results = []
        self.start_time = None

    def run_comparison(self) -> Dict[str, Any]:
        """Run the complete parameter comparison process."""

        self.start_time = time.time()
        self.logger.info("Starting meta-agent parameter comparison")

        try:
            # Main comparison loop
            for iteration in range(self.config.max_examples):
                if self._should_stop():
                    break

                self.logger.info(f"Starting iteration {iteration + 1}/{self.config.max_examples}")

                # Generate input example
                input_example = self._generate_input_example()
                if not input_example:
                    self.logger.warning(f"Failed to generate input example for iteration {iteration + 1}")
                    print(f"\n⚠️  FAILURE: Could not generate input example for iteration {iteration + 1}")
                    print("📊 Attempting to continue with fallback example...")
                    continue

                # Execute workflow with all parameter variations
                workflow_results = self.executor.execute_workflow_variations(input_example)

                # Check for and report any workflow execution failures
                self._report_workflow_failures(workflow_results, iteration + 1)

                # Show execution results summary
                self._display_execution_summary(workflow_results, iteration + 1)

                # Analyze results
                comparison_result = self.analyzer.analyze_results(workflow_results)

                # Store results
                self.comparison_results.append(comparison_result)

                # Display results if significant
                if comparison_result.has_significant_differences:
                    self._display_significant_result(comparison_result, iteration + 1)

                # Log progress
                self.logger.info(f"Iteration {iteration + 1} completed. "
                               f"Inconsistency score: {comparison_result.inconsistency_score:.3f}")

        except Exception as e:
            self.logger.error(f"Error during comparison process: {e}")
            print(f"\n💥 CRITICAL FAILURE: Meta-agent comparison process failed")
            print(f"📋 Error Type: {type(e).__name__}")
            print(f"📝 Error Details: {str(e)}")
            print(f"📊 Completed {len(self.comparison_results)} iterations before failure")

            # Show any partial results if available
            if self.comparison_results:
                print(f"🔍 Partial Results Available:")
                for i, result in enumerate(self.comparison_results):
                    print(f"   Iteration {i+1}: {len(result.workflow_results)} workflow executions")

            import traceback
            print(f"🔧 Stack Trace:")
            traceback.print_exc()
            raise

        finally:
            # Generate final report
            final_report = self._generate_final_report()

            # Save results to file
            self._save_results(final_report)

            self.logger.info("Meta-agent comparison completed")

            return final_report

    def _generate_input_example(self):
        """Generate a new input example using LLM."""

        try:
            examples = self.llm.generate_input_examples(
                self.config,
                [result.input_example for result in self.comparison_results]
            )

            if examples:
                # Select the first example (LLM should provide diverse ones)
                selected_example = examples[0]
                self.generated_examples.append(selected_example)

                self.logger.info(f"Generated input example: {selected_example.get('description', 'No description')}")
                self.logger.info(f"Input Data: {selected_example.get('input', {})}")

                return selected_example.get('input', {})

        except Exception as e:
            self.logger.error(f"Error generating input example: {e}")
            print(f"\n❌ FAILURE: Error generating input example")
            print(f"📋 Error Type: {type(e).__name__}")
            print(f"📝 Error Details: {str(e)}")
            print(f"🔧 Will use fallback example instead")
            raise


    def _report_workflow_failures(self, workflow_results: List, iteration: int) -> None:
        """Report any workflow execution failures with detailed information."""

        failed_results = [r for r in workflow_results if not r.success]

        if failed_results:
            print(f"\n⚠️  WORKFLOW FAILURES in iteration {iteration}:")
            print(f"📊 {len(failed_results)} out of {len(workflow_results)} executions failed")

            for i, result in enumerate(failed_results, 1):
                print(f"\n❌ Failure #{i}:")
                print(f"   📋 Parameters: {result.parameters}")
                print(f"   🔧 Input Data: {result.input_data}")
                print(f"   ⚡ Error: {result.error}")
                print(f"   ⏱️  Execution Time: {result.execution_time:.3f}s")

                if hasattr(result, 'generated_code') and result.generated_code:
                    print(f"   📝 Generated Code:")
                    # Show first few lines of generated code
                    code_lines = result.generated_code.split('\n')[:5]
                    for line in code_lines:
                        print(f"      {line}")
                    if len(result.generated_code.split('\n')) > 5:
                        print(f"      ... ({len(result.generated_code.split('\n')) - 5} more lines)")

                if hasattr(result, 'output') and result.output:
                    print(f"   📤 Partial Output: {str(result.output)[:200]}...")

            print(f"\n✅ {len(workflow_results) - len(failed_results)} executions succeeded")

    def _display_execution_summary(self, workflow_results: List, iteration: int) -> None:
        """Display a summary of execution results for the current iteration."""

        successful_results = [r for r in workflow_results if r.success]

        print(f"\n📈 EXECUTION SUMMARY - Iteration {iteration}:")
        print(f"   🎯 Total Executions: {len(workflow_results)}")
        print(f"   ✅ Successful: {len(successful_results)}")
        print(f"   ❌ Failed: {len(workflow_results) - len(successful_results)}")

        if successful_results:
            avg_time = sum(r.execution_time for r in successful_results) / len(successful_results)
            print(f"   ⏱️  Average Execution Time: {avg_time:.3f}s")

            # Show sample outputs
            print(f"   📤 Sample Successful Results:")
            for i, result in enumerate(successful_results[:2], 1):  # Show first 2 successful results
                output_preview = str(result.output)[:100] if result.output else "No output"
                print(f"      {i}. {result.parameters} → {output_preview}...")

    def _should_stop(self) -> bool:
        """Check if the process should stop based on timeout or other conditions."""

        if self.start_time and time.time() - self.start_time > self.config.timeout_seconds:
            self.logger.info("Stopping due to timeout")
            return True

        # Stop if we have enough significant results
        significant_results = sum(1 for r in self.comparison_results if r.has_significant_differences)
        if significant_results >= self.config.max_examples:  # At least 3 significant differences found
            self.logger.info(f"Stopping after finding {significant_results} significant differences")
            return True

        return False

    def _display_significant_result(self, result: ComparisonResult, iteration: int):
        """Display significant comparison results to the user."""

        print(f"\n{'='*60}")
        print(f"SIGNIFICANT DIFFERENCES FOUND - Iteration {iteration}")
        print(f"{'='*60}")

        print(f"Input Example: {result.input_example}")
        print(f"Inconsistency Score: {result.inconsistency_score:.3f}")
        print(f"Significance: {result.significance_assessment}")

        print("\nKey Differences:")
        for diff in result.key_differences:
            print(f"  • {diff}")

        print("\nConsistency Areas:")
        for consistency in result.consistency_areas:
            print(f"  • {consistency}")

        print("\nDetailed Analysis:")
        print(f"  {result.detailed_analysis}")

        print("\nWorkflow Results Summary:")
        for i, wr in enumerate(result.workflow_results):
            status = "✓" if wr.success else "✗"
            print(f"  {status} Config {i+1}: {wr.parameters} -> {str(wr.output)[:100]}...")

        print(f"{'='*60}\n")

    def _generate_final_report(self) -> Dict[str, Any]:
        """Generate comprehensive final report."""

        total_time = time.time() - self.start_time if self.start_time else 0

        # Summary statistics
        total_iterations = len(self.comparison_results)
        significant_results = [r for r in self.comparison_results if r.has_significant_differences]

        # Average inconsistency score
        avg_inconsistency = (
            sum(r.inconsistency_score for r in self.comparison_results) / total_iterations
            if total_iterations > 0 else 0.0
        )

        # Parameter impact analysis
        parameter_impact = self._analyze_parameter_impact()

        # Most significant finding
        most_significant = max(
            self.comparison_results,
            key=lambda r: r.inconsistency_score,
            default=None
        )

        report = {
            "execution_summary": {
                "total_runtime_seconds": total_time,
                "total_iterations": total_iterations,
                "significant_differences_found": len(significant_results),
                "average_inconsistency_score": avg_inconsistency,
                "configuration": asdict(self.config)
            },
            "significant_findings": [
                {
                    "iteration": i + 1,
                    "input_example": result.input_example,
                    "inconsistency_score": result.inconsistency_score,
                    "key_differences": result.key_differences,
                    "consistency_areas": result.consistency_areas,
                    "significance_assessment": result.significance_assessment,
                    "detailed_analysis": result.detailed_analysis,
                    "workflow_results": [
                        {
                            "parameters": wr.parameters,
                            "success": wr.success,
                            "output": wr.output,
                            "execution_time": wr.execution_time,
                            "error": wr.error
                        }
                        for wr in result.workflow_results
                    ]
                }
                for i, result in enumerate(self.comparison_results)
                # if result.has_significant_differences
            ],
            "parameter_impact_analysis": parameter_impact,
            "most_significant_finding": {
                "inconsistency_score": most_significant.inconsistency_score,
                "input_example": most_significant.input_example,
                "summary": most_significant.significance_assessment
            } if most_significant else None,
            "recommendations": self._generate_recommendations()
        }

        return report

    def _analyze_parameter_impact(self) -> Dict[str, Any]:
        """Analyze which parameters have the most impact on results."""

        parameter_impact = {}

        for param in self.config.parameters:
            param_name = param.name
            impact_scores = []

            for result in self.comparison_results:
                if not result.workflow_results:
                    continue

                # Group results by this parameter's value
                param_groups = {}
                for wr in result.workflow_results:
                    param_value = str(wr.parameters.get(param_name, 'unknown'))
                    if param_value not in param_groups:
                        param_groups[param_value] = []
                    param_groups[param_value].append(wr)

                # Calculate diversity within this parameter
                if len(param_groups) > 1:
                    unique_outputs = set()
                    for group in param_groups.values():
                        for wr in group:
                            if wr.success:
                                unique_outputs.add(str(wr.output))

                    # Impact score based on output diversity
                    impact_score = len(unique_outputs) / len(result.workflow_results)
                    impact_scores.append(impact_score)

            parameter_impact[param_name] = {
                "average_impact_score": sum(impact_scores) / len(impact_scores) if impact_scores else 0.0,
                "max_impact_score": max(impact_scores) if impact_scores else 0.0,
                "options_tested": param.options,
                "description": param.description
            }

        # Sort by impact
        sorted_impact = dict(sorted(
            parameter_impact.items(),
            key=lambda x: x[1]["average_impact_score"],
            reverse=True
        ))

        return sorted_impact

    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on findings."""

        recommendations = []

        significant_count = sum(1 for r in self.comparison_results if r.has_significant_differences)
        total_count = len(self.comparison_results)

        if significant_count == 0:
            recommendations.append(
                "No significant parameter differences detected. "
                "Consider testing with more diverse input examples or different parameter ranges."
            )
        elif significant_count / total_count > 0.7:
            recommendations.append(
                "High variability detected across parameter configurations. "
                "Consider standardizing parameter choices or documenting expected variations."
            )
        else:
            recommendations.append(
                f"Moderate variability detected ({significant_count}/{total_count} cases). "
                "Review significant cases to understand parameter impact."
            )

        # Parameter-specific recommendations
        param_impact = self._analyze_parameter_impact()
        high_impact_params = [
            name for name, data in param_impact.items()
            if data["average_impact_score"] > 0.5
        ]

        if high_impact_params:
            recommendations.append(
                f"Parameters with high impact on results: {', '.join(high_impact_params)}. "
                "Consider careful selection of these parameters."
            )

        return recommendations

    def _save_results(self, report: Dict[str, Any]):
        """Save results to file."""

        try:
            with open(self.config.output_file, 'w') as f:
                json.dump(report, f, indent=2, default=str)

            self.logger.info(f"Results saved to {self.config.output_file}")

        except Exception as e:
            self.logger.error(f"Error saving results: {e}")

    def _create_llm_interface(self) -> LLMInterface:
        """Create LLM interface based on configuration."""

        return create_llm_interface(
            self.config.llm_provider,
            self.config.llm_api_key,
            self.config.llm_model
        )

    def _create_executor(self) -> WorkflowExecutor:
        """Create workflow executor."""

        # Use safe executor with timeout and pass LLM interface for code generation
        return SafeWorkflowExecutor(self.config, self.llm, timeout_per_execution=6000)

    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration."""

        logger = logging.getLogger("meta_agent")
        logger.setLevel(logging.INFO if self.config.verbose else logging.WARNING)

        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger


def run_meta_agent(config: WorkflowConfiguration) -> Dict[str, Any]:
    """Convenience function to run the meta-agent with a configuration."""

    agent = MetaAgent(config)
    return agent.run_comparison()
