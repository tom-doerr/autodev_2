"""Tests for the code_modifier module."""

import os
import tempfile
from unittest.mock import MagicMock, patch

import pytest

from codeagent.code_modifier import CodeModifierAgent
from codeagent.model import ModelManager


@pytest.fixture
def temp_project():
    """Create a temporary project directory."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a sample Python file
        with open(os.path.join(temp_dir, "sample.py"), "w", encoding="utf-8") as f:
            f.write("def hello():\n    return 'Hello, World!'\n")

        yield temp_dir


def test_code_modifier_init():
    """Test CodeModifierAgent initialization."""
    modifier = CodeModifierAgent()
    assert modifier is not None
    assert modifier.rope_script_generator is not None


def test_modify_file(temp_project):  # pylint: disable=redefined-outer-name
    """Test modify_file method."""
    modifier = CodeModifierAgent()

    # Create a file to modify
    file_path = os.path.join(temp_project, "test.py")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write("def hello():\n    return 'Hello, World!'\n")

    # Mock the rope_script_generator to return a fixed script
    mock_generator = MagicMock()
    mock_generator.return_value = """
from rope.base.project import Project

def change_function(project_path, file_path):
    # Create a Rope project in the current directory
    project = Project(project_path)
    
    # Get the file resource
    source_code = project.get_resource(file_path)
    
    # Read the current content
    source = source_code.read()
    
    # Create the modified content
    new_source = "def hello():\\n    return 'Hello, Modified!'\\n"
    
    # Write the modified content back to the file
    source_code.write(new_source)
    
    # Return the modified content
    return new_source
"""
    modifier.rope_script_generator = mock_generator

    # Mock the _execute_rope_script method to avoid actually running the script
    with patch.object(modifier, "_execute_rope_script") as mock_execute:
        mock_execute.return_value = "def hello():\n    return 'Hello, Modified!'\n"

        # Test modifying a file
        result = modifier.modify_file(file_path, "Change the greeting")

        # Check the result
        assert "Hello, Modified!" in result

        # Check that the generator was called with the right arguments
        mock_generator.assert_called_once()
        assert "Hello, World!" in mock_generator.call_args[0][0]
        assert "Change the greeting" in mock_generator.call_args[0][1]


def test_generate_code():
    """Test generate_code method."""
    modifier = CodeModifierAgent()

    # Test generating code
    instructions = "Create a function that calculates the factorial"
    result = modifier.generate_code(instructions)

    # Check the result
    assert "factorial" in result
    assert "return 1 if n <= 1 else n * factorial(n-1)" in result


def test_get_default_code_modifier():
    """Test get_default_code_modifier function."""
    with patch.dict(os.environ, {"CODEAGENT_MODEL": "test-model"}):
        modifier = modifier.get_default_code_modifier()
        assert modifier.model_name == "test-model"

    # Test without environment variable
    with patch.dict(os.environ, {}, clear=True):
        modifier = modifier.get_default_code_modifier()
        assert modifier.model_name is None


def test_execute_rope_script_error():
    """Test error handling in _execute_rope_script method."""
    modifier = CodeModifierAgent()

    with tempfile.TemporaryDirectory() as temp_dir:
        file_path = os.path.join(temp_dir, "test.py")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("def hello():\n    return 'Hello, World!'\n")

        # Create an invalid script that will raise an exception
        invalid_script = "invalid python code"

        # Test that ValueError is raised
        with pytest.raises(ValueError):
            # pylint: disable=protected-access
            modifier._execute_rope_script(invalid_script, temp_dir, file_path)


def test_run_script_function_fallback():
    """Test fallback to refactor_code in _run_script_function."""
    modifier = CodeModifierAgent()

    # Create a mock module with refactor_code but no change_function
    mock_module = MagicMock()
    # Remove the change_function attribute completely
    delattr(mock_module, "change_function")
    mock_module.refactor_code = MagicMock(return_value="Modified code")

    # pylint: disable=protected-access
    result = modifier._run_script_function(mock_module, "project_path", "file_path")
    assert result == "Modified code"
    mock_module.refactor_code.assert_called_once_with("project_path", "file_path")


def test_run_script_function_error():
    """Test error handling in _run_script_function."""
    modifier = CodeModifierAgent()

    # Create a mock module with neither change_function nor refactor_code
    mock_module = MagicMock()
    # Remove both attributes completely
    delattr(mock_module, "change_function")
    delattr(mock_module, "refactor_code")

    with pytest.raises(
        ValueError, match="Rope script does not contain a change_function or refactor_code function"
    ):
        # pylint: disable=protected-access
        modifier._run_script_function(mock_module, "project_path", "file_path")


def test_get_relative_path():
    """Test _get_relative_path method."""
    modifier = CodeModifierAgent()

    # Test with absolute file path
    abs_file_path = "/home/user/project/file.py"
    project_path = "/home/user/project"
    # pylint: disable=protected-access
    rel_path = modifier._get_relative_path(abs_file_path, project_path)
    assert rel_path == "file.py"

    # Test with relative file path
    rel_file_path = "file.py"
    rel_path = modifier._get_relative_path(rel_file_path, project_path)
    assert rel_path == "file.py"


def test_load_module_from_file():
    """Test _load_module_from_file method."""
    modifier = CodeModifierAgent()
    
    # Create a valid Python module file
    with tempfile.NamedTemporaryFile(suffix=".py", delete=False) as temp_file:
        temp_file.write(b"def test_function():\n    return 'test'\n")
        temp_file_path = temp_file.name
    
    try:
        # Test loading a valid module
        # pylint: disable=protected-access
        with patch('importlib.util.spec_from_file_location') as mock_spec:
            # Create a mock spec
            mock_spec.return_value = MagicMock()
            # Create a mock module
            mock_module = MagicMock()
            mock_module.test_function = lambda: 'test'
            # Set up the mock loader to return our mock module
            mock_spec.return_value.loader.exec_module = lambda m: None
            
            # Patch importlib.util.module_from_spec to return our mock module
            with patch('importlib.util.module_from_spec', return_value=mock_module):
                module = modifier._load_module_from_file(temp_file_path)
                assert hasattr(module, "test_function")
                assert module.test_function() == 'test'
        
        # Test with an invalid path
        with patch('importlib.util.spec_from_file_location', return_value=None):
            with pytest.raises(ImportError):
                # pylint: disable=protected-access
                modifier._load_module_from_file("/non/existent/path.py")
    finally:
        # Clean up
        os.unlink(temp_file_path)


def test_execute_rope_script_with_actual_file():
    """Test _execute_rope_script method with an actual file."""
    modifier = CodeModifierAgent()
    
    with tempfile.TemporaryDirectory() as temp_dir:
        file_path = os.path.join(temp_dir, "test.py")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("def hello():\n    return 'Hello, World!'\n")
        
        # Create a valid script
        script = """
import os

def change_function(project_path, file_path):
    # Just read the file and return its content
    with open(os.path.join(project_path, file_path), 'r') as f:
        return f.read()
"""
        
        # Mock the _load_module_from_file method to avoid actual file system operations
        with patch.object(modifier, '_load_module_from_file') as mock_load:
            # Create a mock module with a change_function
            mock_module = MagicMock()
            mock_module.change_function = lambda p, f: "Modified content"
            mock_load.return_value = mock_module
            
            # Test executing the script
            # pylint: disable=protected-access
            result = modifier._execute_rope_script(script, temp_dir, file_path)
            # pylint: enable=protected-access
            assert result == "Modified content"


def test_run_script_function_no_functions():
    """Test _run_script_function with a module that has no required functions."""
    modifier = CodeModifierAgent()
    
    # Create a mock module with neither change_function nor refactor_code
    mock_module = MagicMock(spec=[])  # Empty spec means no attributes
    
    # Test that ValueError is raised
    with pytest.raises(ValueError, match="Rope script does not contain"):
        # pylint: disable=protected-access
        modifier._run_script_function(mock_module, "project_path", "file_path")
