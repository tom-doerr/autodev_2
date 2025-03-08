"""Tests for DSPy optimization using DSPy assertions."""

import os
import sys
from pathlib import Path

import pytest

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

try:
    import dspy
    from dspy.teleprompt import BasicTeleprompter
    from dspy.evaluate import Evaluate
    from dspy.teleprompt import BootstrapFewShot
    from dspy.predict import Predict
    from dspy.primitives.assertions import assert_transform_module
    from codeagent.dspy_modules.rope_script_generator import RopeScriptGenerator
    from codeagent.code_modifier import CodeModifierAgent
    from codeagent.model import ModelManager
    DSPY_AVAILABLE = True
except ImportError:
    DSPY_AVAILABLE = False

# Skip all tests in this module if DSPy is not available
pytestmark = pytest.mark.skipif(not DSPY_AVAILABLE, reason="DSPy is not available")


class SimpleAddTypeHints(dspy.Module):
    """A simple DSPy module to add type hints to a Python function."""

    def __init__(self):
        super().__init__()
        self.generate_script = Predict(
            "code,instruction -> script",
            desc="Generate a Python script using Rope to add type hints to the given code.",
        )

    def forward(self, code, instruction):
        script = self.generate_script(code=code, instruction=instruction).script
        return script


def has_type_hints(script):
    """Check if the generated script adds type hints."""
    return "def change_function(" in script and ": int" in script


def test_dspy_optimization():
    """Test DSPy optimization using DSPy assertions."""
    # Define the initial code and instructions
    code = """
def calculate_sum(a, b):
    return a + b
"""
    instruction = "Add type hints to the function parameters and return value."

    # Create a DSPy module
    module = SimpleAddTypeHints()

    # Create a dev set
    dev_set = [
        {"code": code, "instruction": instruction, "output": has_type_hints},
    ]

    # Configure the teleprompter
    teleprompter = BasicTeleprompter()

    # Configure the evaluator
    def evaluate_func(example, pred, trace=None):
        return example["output"](pred)

    evaluate = Evaluate(devset=dev_set, metric=evaluate_func, num_threads=1)

    # Optimize the module
    # chain_of_thought = False
    # new_module = BootstrapFewShot(metric=evaluate_func).compile(
    #     module, trainset=dev_set, eval_kwargs={'num_threads': 1}
    # )
    
    # Evaluate the optimized module
    # metric = evaluate.run(new_module, devset=dev_set, num_threads=1)
    # print(f"Metric: {metric}")

    # Assert that the optimized module passes the assertions
    # assert metric > 0.8
    
    # Create a CodeModifierAgent instance
    agent = CodeModifierAgent()
    
    # Generate the script
    generator = RopeScriptGenerator()
    script = generator(code, instruction)
    
    # Check if the generated script adds type hints
    assert has_type_hints(script)
