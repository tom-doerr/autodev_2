"""Test script to demonstrate the CodeModifierAgent."""

import os
import sys
import tempfile

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from codeagent.code_modifier import CodeModifierAgent


def test_modify_existing_code():
    """Test modifying existing code with CodeModifierAgent."""
    # Create a CodeModifierAgent instance
    agent = CodeModifierAgent()

    # Path to the sample code
    sample_code_path = os.path.join(os.path.dirname(__file__), "sample_code.py")

    # Instructions for modifying the DataProcessor class
    instructions = """
    Enhance the DataProcessor class by:
    1. Adding a new method called 'filter_data' that takes a condition function and returns filtered data
    2. Adding type hints to all methods
    3. Improving the docstrings with parameter and return type descriptions
    """

    # Modify the file
    print(f"Modifying file: {sample_code_path}")
    modified_code = agent.modify_file(sample_code_path, instructions)

    # Print the modified code
    print("\nModified code:")
    print("-" * 80)
    print(modified_code)
    print("-" * 80)

    # Create a copy of the modified file
    modified_file_path = os.path.join(os.path.dirname(__file__), "modified_sample_code.py")
    with open(modified_file_path, "w", encoding="utf-8") as f:
        f.write(modified_code)

    print(f"\nModified code saved to: {modified_file_path}")


def test_generate_new_code():
    """Test generating new code with CodeModifierAgent."""
    # Create a CodeModifierAgent instance
    agent = CodeModifierAgent()

    # Instructions for generating a new utility module
    instructions = """
    Create a utility module with the following functions:
    1. A function to calculate the median of a list of numbers
    2. A function to find the most frequent item in a list
    3. A function to check if a string is a palindrome
    
    All functions should have proper type hints, docstrings, and error handling.
    """

    # Generate the code
    print("\nGenerating new code...")
    generated_code = agent.generate_code(instructions)

    # Print the generated code
    print("\nGenerated code:")
    print("-" * 80)
    print(generated_code)
    print("-" * 80)

    # Save the generated code to a file
    generated_file_path = os.path.join(os.path.dirname(__file__), "utils.py")
    with open(generated_file_path, "w", encoding="utf-8") as f:
        f.write(generated_code)

    print(f"\nGenerated code saved to: {generated_file_path}")


if __name__ == "__main__":
    test_modify_existing_code()
    test_generate_new_code()
