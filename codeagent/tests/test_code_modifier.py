"""Tests for the code_modifier module."""

import os
import tempfile
from unittest.mock import MagicMock

import pytest

from codeagent.code_modifier import CodeModifier


@pytest.fixture
def temp_project():
    """Create a temporary project for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a simple Python file
        file_path = os.path.join(temp_dir, "example.py")
        with open(file_path, "w") as f:
            f.write("def hello():\n    return 'Hello, World!'\n")
        
        yield temp_dir, file_path


def test_code_modifier_init():
    """Test CodeModifier initialization."""
    model_manager = MagicMock()
    modifier = CodeModifier(model_manager)
    
    assert modifier.model_manager == model_manager
    assert modifier.project is None


def test_load_project(temp_project):
    """Test load_project method."""
    temp_dir, _ = temp_project
    
    modifier = CodeModifier(MagicMock())
    modifier.load_project(temp_dir)
    
    assert modifier.project is not None
    # Normalize paths by removing trailing slashes for comparison
    assert os.path.normpath(modifier.project.root.real_path) == os.path.normpath(temp_dir)


def test_modify_file(temp_project):
    """Test modify_file method."""
    _, file_path = temp_project
    
    # Mock the model manager
    model_manager = MagicMock()
    model_manager.get_completion.return_value = "def hello():\n    return 'Hello, Modified!'\n"
    
    modifier = CodeModifier(model_manager)
    result = modifier.modify_file(file_path, "Change the return value")
    
    # Check that the file was modified
    assert "Modified" in result
    
    # Check that the model was called with the correct prompt
    model_manager.get_completion.assert_called_once()
    prompt = model_manager.get_completion.call_args[0][0]
    assert "Change the return value" in prompt
    assert "def hello():" in prompt


def test_create_modification_prompt():
    """Test _create_modification_prompt method."""
    modifier = CodeModifier(MagicMock())
    
    code = "def hello():\n    return 'Hello, World!'\n"
    instruction = "Change the return value"
    
    prompt = modifier._create_modification_prompt(code, instruction)
    
    assert code in prompt
    assert instruction in prompt
    assert "ORIGINAL CODE:" in prompt
    assert "INSTRUCTION:" in prompt
