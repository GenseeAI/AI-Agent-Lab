import os
import dotenv
dotenv.load_dotenv()

import dspy

model = dspy.LM('gpt-4o', max_tokens=1000)

dspy.configure(lm=model)


class Reasoning(dspy.Signature):
    """You are an expert at providing guidance for a coding task.
    
    Given an incomplete python function with its docstring. Reason about what the function should do step by step, no need to complete the function.
    """
    incomplete_function: str = dspy.InputField()
    guidance: str = dspy.OutputField()
    
class Coding(dspy.Signature):
    """You are an expert at coding.
    
    Your task is to complete the given python function by using the information from its docstring and provided tips.
    """
    incomplete_function: str = dspy.InputField()
    guidance: str = dspy.InputField()
    function_body: str = dspy.OutputField(
        desc="Only the function body should be returned, and wrapped in <result> and </result> tags."
    )

class CodeGen(dspy.Module):
    def __init__(self):
        super().__init__()
        
        self.reasoning = dspy.Predict(Reasoning)
        self.coding = dspy.Predict(Coding)

    def forward(self, task: str) -> str:
        guidance = self.reasoning(incomplete_function=task).guidance
        # print("Guidance:", guidance)
        func_body = self.coding(
            incomplete_function=task,
            guidance=guidance
        ).function_body
        return func_body
    
workflow = CodeGen()

def codegen_workflow(task):
    result = workflow(task=task)
    return result
    
# if __name__ == "__main__":
#     task = "\n\ndef truncate_number(number: float) -> float:\n    \"\"\" Given a positive floating point number, it can be decomposed into\n    and integer part (largest integer smaller than given number) and decimals\n    (leftover part always smaller than 1).\n\n    Return the decimal part of the number.\n    >>> truncate_number(3.5)\n    0.5\n    \"\"\"\n"
#     print("Task:", task)
#     result = workflow('test', task=task)
#     print(result)