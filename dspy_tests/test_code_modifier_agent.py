"""Test the CodeModifierAgent with DSPy."""

import os
import sys
import tempfile

# Add the codeagent package to the Python path
sys.path.append('/home/tom/git/autodev_2/codeagent')

from codeagent.code_modifier import CodeModifierAgent
from codeagent.model import DSPY_AVAILABLE

def test_code_modifier_agent():
    """Test the CodeModifierAgent."""
    # Print Python version and environment info
    print(f"Python version: {sys.version}")
    print(f"PYTHONPATH: {os.environ.get('PYTHONPATH', '')}")
    print(f"DSPy available: {DSPY_AVAILABLE}")
    
    # Create a CodeModifierAgent instance
    agent = CodeModifierAgent("openrouter/google/gemini-2.0-flash-001")
    
    # Test code generation
    instructions = """
    Create a Python function that:
    1. Takes a list of integers as input
    2. Returns the sum of all even numbers in the list
    3. Include comments and docstrings
    """
    
    generated_code = agent.generate_code(instructions)
    print(f"Generated code:\n{generated_code}")
    
    # Test code modification
    original_code = """
def sum_numbers(numbers):
    total = 0
    for num in numbers:
        total += num
    return total
    """
    
    modification_instructions = """
    Modify the function to:
    1. Only sum even numbers
    2. Add proper docstrings and comments
    3. Add type hints
    """
    
    # Create a temporary file to test modify_file
    with tempfile.NamedTemporaryFile(suffix='.py', mode='w', delete=False) as temp_file:
        temp_file.write(original_code)
        temp_file_path = temp_file.name
    
    try:
        # Use modify_file instead of modify_code
        modified_code = agent.modify_file(temp_file_path, modification_instructions)
        print(f"Modified code:\n{modified_code}")
    finally:
        # Clean up the temporary file
        os.unlink(temp_file_path)
    
    return generated_code, modified_code

if __name__ == "__main__":
    test_code_modifier_agent()
