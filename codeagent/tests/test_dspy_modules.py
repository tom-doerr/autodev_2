"""Tests for the DSPy modules in codeagent."""

import os
import sys
import pytest
from unittest.mock import patch, MagicMock

from codeagent.dspy_modules import RopeScriptGenerator, DSPY_AVAILABLE


class TestRopeScriptGenerator:
    """Tests for the RopeScriptGenerator class."""

    @pytest.fixture
    def mock_dspy_available(self):
        """Fixture to mock DSPy as available."""
        with patch('codeagent.dspy_modules.DSPY_AVAILABLE', True):
            yield

    @pytest.fixture
    def mock_dspy_unavailable(self):
        """Fixture to mock DSPy as unavailable."""
        with patch('codeagent.dspy_modules.DSPY_AVAILABLE', False):
            yield

    @pytest.fixture
    def mock_dspy_lm(self):
        """Fixture to mock DSPy LM."""
        mock_lm = MagicMock()
        mock_lm.return_value = "# Generated Rope script\ndef refactor_code(project_path, file_path):\n    # Implementation\n    pass"
        
        with patch('dspy.LM', return_value=mock_lm) as mock_lm_class, \
             patch('dspy.settings') as mock_settings:
            mock_settings.lm = None
            yield mock_lm_class, mock_lm

    def test_import_error_handling(self):
        """Test the import error handling in the module."""
        # Create a mock module to simulate the ImportError
        mock_module = type('MockModule', (), {'__getattr__': lambda self, name: exec('raise ImportError("No module named dspy")')})()
        
        # Patch sys.modules to include our mock module
        with patch.dict('sys.modules', {'dspy': mock_module}):
            # Force a reload of the module to trigger the ImportError handling
            import importlib
            from codeagent import dspy_modules
            importlib.reload(dspy_modules)
            
            # Verify DSPY_AVAILABLE is False
            assert dspy_modules.DSPY_AVAILABLE is False

    def test_init_with_model_name(self, mock_dspy_available, mock_dspy_lm):
        """Test initialization with a specific model name."""
        mock_lm_class, _ = mock_dspy_lm
        
        generator = RopeScriptGenerator(model_name="test-model")
        assert generator.model_name == "test-model"
        
        # Verify dspy.LM was called with the correct model name
        mock_lm_class.assert_called_once_with("test-model")

    def test_init_without_model_name(self, mock_dspy_available, mock_dspy_lm):
        """Test initialization without a model name."""
        mock_lm_class, _ = mock_dspy_lm
        
        with patch.dict(os.environ, {"CODEAGENT_MODEL": "env-model"}):
            generator = RopeScriptGenerator()
            assert generator.model_name is None
            
            # Verify dspy.LM was called with the environment variable
            mock_lm_class.assert_called_once_with("env-model")

    def test_init_with_default_model(self, mock_dspy_available, mock_dspy_lm):
        """Test initialization with default model when no env var is set."""
        mock_lm_class, _ = mock_dspy_lm
        
        with patch.dict(os.environ, {}, clear=True):
            generator = RopeScriptGenerator()
            assert generator.model_name is None
            
            # Verify dspy.LM was called with the default model
            mock_lm_class.assert_called_once_with("openrouter/google/gemini-2.0-flash-001")

    def test_init_with_existing_lm(self, mock_dspy_available):
        """Test initialization when dspy.settings.lm is already set."""
        mock_existing_lm = MagicMock()
        
        with patch('dspy.LM') as mock_lm_class, \
             patch('dspy.settings') as mock_settings:
            mock_settings.lm = mock_existing_lm
            
            generator = RopeScriptGenerator()
            assert generator.model_name is None
            
            # Verify dspy.LM was not called since settings.lm is already set
            mock_lm_class.assert_not_called()

    def test_call_with_dspy_available(self, mock_dspy_available, mock_dspy_lm):
        """Test calling the generator when DSPy is available."""
        _, mock_lm = mock_dspy_lm
        
        with patch('dspy.settings.lm', mock_lm):
            generator = RopeScriptGenerator()
            
            code = "def example():\n    return 42"
            instructions = "Rename the function to calculate_answer"
            
            result = generator(code, instructions)
            
            # Verify the LM was called with the correct prompt
            mock_lm.assert_called_once()
            call_args = mock_lm.call_args[1]['prompt']
            assert "instructions" in call_args
            assert "Rename the function to calculate_answer" in call_args
            assert "def example():" in call_args
            
            # Verify the result is as expected
            assert "refactor_code" in result

    def test_call_with_dspy_unavailable(self, mock_dspy_unavailable):
        """Test calling the generator when DSPy is unavailable."""
        generator = RopeScriptGenerator()
        
        with pytest.raises(ImportError, match="DSPy is required for RopeScriptGenerator"):
            generator("code", "instructions")

    def test_call_with_markdown_response(self, mock_dspy_available, mock_dspy_lm):
        """Test handling of markdown code blocks in the response."""
        _, mock_lm = mock_dspy_lm
        mock_lm.return_value = "```python\ndef refactor_code(project_path, file_path):\n    # Implementation with markdown\n    pass\n```"
        
        with patch('dspy.settings.lm', mock_lm):
            generator = RopeScriptGenerator()
            result = generator("code", "instructions")
            
            # Verify the markdown was stripped correctly
            assert result == "def refactor_code(project_path, file_path):\n    # Implementation with markdown\n    pass"
            assert "```" not in result
            
    def test_call_with_generic_markdown_response(self, mock_dspy_available, mock_dspy_lm):
        """Test handling of generic markdown code blocks without language specifier."""
        _, mock_lm = mock_dspy_lm
        mock_lm.return_value = "```\ndef refactor_code(project_path, file_path):\n    # Implementation with generic markdown\n    pass\n```"
        
        with patch('dspy.settings.lm', mock_lm):
            generator = RopeScriptGenerator()
            result = generator("code", "instructions")
            
            # Verify the markdown was stripped correctly
            assert result == "def refactor_code(project_path, file_path):\n    # Implementation with generic markdown\n    pass"
            assert "```" not in result

    def test_call_with_list_response(self, mock_dspy_available, mock_dspy_lm):
        """Test handling of list responses."""
        _, mock_lm = mock_dspy_lm
        mock_lm.return_value = ["def refactor_code(project_path, file_path):\n    # Implementation as list\n    pass"]
        
        with patch('dspy.settings.lm', mock_lm):
            generator = RopeScriptGenerator()
            result = generator("code", "instructions")
            
            # Verify the list was handled correctly
            assert result == "def refactor_code(project_path, file_path):\n    # Implementation as list\n    pass"

    def test_call_with_empty_response(self, mock_dspy_available, mock_dspy_lm):
        """Test handling of empty responses."""
        _, mock_lm = mock_dspy_lm
        mock_lm.return_value = []
        
        with patch('dspy.settings.lm', mock_lm):
            generator = RopeScriptGenerator()
            result = generator("code", "instructions")
            
            # Verify empty list returns empty string
            assert result == ""
            
    def test_extract_script_from_response_with_none(self, mock_dspy_available):
        """Test extracting script from None response."""
        generator = RopeScriptGenerator(model_name="test-model")
        result = generator._extract_script_from_response(None)
        assert result == ""
        
    def test_extract_script_from_response_with_object(self, mock_dspy_available):
        """Test extracting script from an object that's not a string or list."""
        generator = RopeScriptGenerator(model_name="test-model")
        
        # Test with a number
        result = generator._extract_script_from_response(42)
        assert result == "42"
        
        # Test with a custom object
        class CustomResponse:
            def __str__(self):
                return "custom response string"
        
        custom_obj = CustomResponse()
        result = generator._extract_script_from_response(custom_obj)
        assert result == "custom response string"
        
    def test_extract_script_from_response_with_plain_string(self, mock_dspy_available):
        """Test extracting script from a plain string without markdown."""
        generator = RopeScriptGenerator(model_name="test-model")
        result = generator._extract_script_from_response("def example():\n    return 42")
        assert result == "def example():\n    return 42"
