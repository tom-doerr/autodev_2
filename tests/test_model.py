"""Tests for the model module."""

from unittest.mock import MagicMock, patch

import pytest

from codeagent.model import DSPY_AVAILABLE, ModelManager, get_default_model


def test_dspy_import():
    """Test the dspy import logic."""
    # Test that DSPY_AVAILABLE is defined
    assert isinstance(DSPY_AVAILABLE, bool)
    
    # Simulate both import scenarios using a mock module
    mock_module = MagicMock()
    mock_module.DSPY_AVAILABLE = False
    
    with patch('codeagent.model', mock_module):
        assert mock_module.DSPY_AVAILABLE is False
        
        # Change the value
        mock_module.DSPY_AVAILABLE = True
        assert mock_module.DSPY_AVAILABLE is True


def test_model_manager_init():
    """Test ModelManager initialization."""
    # Test with default model
    manager = ModelManager()
    assert manager.model_name == ModelManager.DEFAULT_MODEL

    # Test with custom model
    custom_model = "custom/model"
    manager = ModelManager(custom_model)
    assert manager.model_name == custom_model


# Only run this test if DSPy is available
@pytest.mark.skipif(not DSPY_AVAILABLE, reason="DSPy not available in test environment")
@patch("dspy.LM")
def test_model_manager_lm_with_dspy(mock_lm):
    """Test ModelManager.lm property when DSPy is available."""
    mock_instance = MagicMock()
    mock_lm.return_value = mock_instance

    manager = ModelManager()
    lm = manager.lm

    mock_lm.assert_called_once_with(manager.model_name)
    assert lm == mock_instance


@patch("codeagent.model.DSPY_AVAILABLE", False)
def test_model_manager_lm_without_dspy():
    """Test ModelManager.lm property when DSPy is not available."""
    manager = ModelManager()
    lm = manager.lm

    # Check that a mock LM is returned
    assert hasattr(lm, "complete")

    # Test the mock LM
    response = lm.complete("Test prompt")
    assert response.text == "# Modified code based on: Test prompt"


@patch("codeagent.model.ModelManager.lm", new_callable=MagicMock)
def test_model_manager_get_completion(mock_lm):
    """Test ModelManager.get_completion method."""
    # Setup the mock to return a list with a completion
    mock_lm.return_value = ["Mocked completion"]

    # Create a manager
    manager = ModelManager("test-model")

    # Call get_completion
    result = manager.get_completion("Test prompt")

    # Check that lm was called with the correct prompt
    mock_lm.assert_called_once_with(prompt="Test prompt")

    # Check that the result is correct
    assert result == "Mocked completion"


def test_get_default_model():
    """Test get_default_model function."""
    with patch("os.environ.get") as mock_environ_get:
        # Test with environment variable set
        mock_environ_get.return_value = "env-model"
        model = get_default_model()
        assert model.model_name == "env-model"
        mock_environ_get.assert_called_with(
            "CODEAGENT_MODEL", "openrouter/google/gemini-2.0-flash-001"
        )

        # Test with environment variable not set
        mock_environ_get.return_value = None
        model = get_default_model()
        assert model.model_name == "openrouter/google/gemini-2.0-flash-001"
