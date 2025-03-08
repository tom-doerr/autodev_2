"""Test DSPy assertions in RopeScriptGenerator."""

import os
import sys
import tempfile

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from codeagent.dspy_modules.rope_script_generator import Assert, RopeScriptGenerator


def test_rope_script_generator_assertions():
    """Test that RopeScriptGenerator validates scripts with assertions."""
    # Create a RopeScriptGenerator instance
    generator = RopeScriptGenerator()

    # Test generating a script for a simple function
    file_content = """
def add(a, b):
    return a + b
"""

    instructions = "Modify the function to add type hints"

    # Generate the script
    script = generator(file_content, instructions)

    print("\nGenerated script:")
    print("-" * 80)
    print(script)
    print("-" * 80)

    # Verify that the script contains the required elements
    assert "def change_function(project_path, file_path):" in script
    assert "from rope.base.project import Project" in script
    assert "project = Project(project_path)" in script
    assert "project.get_resource(file_path)" in script
    assert "return " in script

    # Test that assertions work by creating an invalid script
    try:
        # This should raise a ValueError because the script is invalid
        Assert(False, "Test assertion")
        assert False, "Assertion should have raised a ValueError"
    except ValueError as e:
        print(f"Caught expected ValueError: {e}")

    # Test generating a new file script
    instructions = "Create a new file with: A function to calculate the factorial of a number"

    # Generate the script
    new_file_script = generator("", "Create a new file with: " + instructions)

    print("\nGenerated new file script:")
    print("-" * 80)
    print(new_file_script)
    print("-" * 80)

    # Verify that the script contains the required elements
    assert "def change_function(project_path, file_path):" in new_file_script
    assert "from rope.base.project import Project" in new_file_script
    assert "project = Project(project_path)" in new_file_script
    assert "project.get_resource(file_path)" in new_file_script
    assert "return " in new_file_script

    print("\nAll assertions passed!")


if __name__ == "__main__":
    test_rope_script_generator_assertions()
