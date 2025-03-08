"""Test the RopeScriptGenerator with assertions."""

import os
import sys

import pytest

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

# Import after modifying the path
from codeagent.dspy_modules.rope_script_generator import (  # pylint: disable=wrong-import-position
    Assert,
    RopeScriptGenerator,
)


def test_assert_class():
    """Test that our Assert class works correctly."""
    # Test that Assert works when condition is True
    Assert(True, "This should not raise an error")

    # Test that Assert raises ValueError when condition is False
    with pytest.raises(ValueError, match="Assertion failed: This should raise an error"):
        Assert(False, "This should raise an error")


def test_rope_script_generator_validation():
    """Test that RopeScriptGenerator validates scripts correctly."""
    generator = RopeScriptGenerator()

    # Create a valid script
    valid_script = """
from rope.base.project import Project

def change_function(project_path, file_path):
    project = Project(project_path)
    resource = project.get_resource(file_path)
    source = resource.read()
    new_source = source.replace('old', 'new')
    return new_source
"""

    # This should not raise an error
    # pylint: disable=protected-access
    generator._validate_script(valid_script)

    # Create an invalid script (missing required elements)
    invalid_script = """
def wrong_function_name(project_path, file_path):
    # Missing Project import
    # Missing project = Project(project_path)
    # Missing project.get_resource(file_path)
    return "Modified code"
"""

    # This should raise a ValueError
    with pytest.raises(
        ValueError, match="Assertion failed: Script must define a 'change_function' function"
    ):
        generator._validate_script(invalid_script)

    # Create a script with syntax error
    syntax_error_script = """
def change_function(project_path, file_path):
    # Missing import
    project = Project(project_path)
    resource = project.get_resource(file_path)
    # Syntax error: missing closing parenthesis
    print("Hello"
    return "Modified code"
"""

    # This should raise a ValueError with a validation error message first
    with pytest.raises(
        ValueError, match="Assertion failed: Script must import 'Project' from 'rope.base.project'"
    ):
        generator._validate_script(syntax_error_script)


def test_rope_script_generation():
    """Test that RopeScriptGenerator generates valid scripts."""
    generator = RopeScriptGenerator()

    # Test generating a script for a simple function
    file_content = """
def add(a, b):
    return a + b
"""

    instructions = "Modify the function to add type hints"

    # Generate the script
    script = generator(file_content, instructions)

    # Verify that the script contains the required elements
    assert "def change_function(project_path, file_path):" in script
    assert "from rope.base.project import Project" in script
    assert "project = Project(project_path)" in script
    assert "project.get_resource(file_path)" in script
    assert "return " in script
