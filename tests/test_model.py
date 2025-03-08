"""Tests for the model module."""

import os
from unittest.mock import MagicMock, patch

import pytest

from codeagent.model import ModelManager, get_default_model, DSPY_AVAILABLE


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
def test_model_manager_lm_with_dspy():
    """Test ModelManager.lm property when DSPy is available."""
    manager = ModelManager()
    lm = manager.lm
    
    # Check that a real DSPy LM is returned
    assert hasattr(lm, '__call__')  # DSPy LM has __call__ method
    assert hasattr(lm, 'model')     # DSPy LM has model attribute
    assert manager.model_name in str(lm.model)  # Model name should be in the model string representation


@patch('codeagent.model.DSPY_AVAILABLE', False)
def test_model_manager_lm_without_dspy():
    """Test ModelManager.lm property when DSPy is not available."""
    manager = ModelManager()
    lm = manager.lm
    
    # Check that a mock LM is returned
    assert hasattr(lm, 'complete')
    
    # Test the mock LM
    response = lm.complete("Test prompt")
    assert response.text == "# Modified code based on: Test prompt"


@patch('codeagent.model.DSPY_AVAILABLE', True)
def test_model_manager_get_completion():
    """Test ModelManager.get_completion method."""
    manager = ModelManager()
    
    # Mock the lm property
    mock_lm = MagicMock()
    mock_lm.complete.return_value.text = "Mocked completion"
    manager._lm = mock_lm
    
    completion = manager.get_completion("Test prompt")
    
    # Check that the completion was returned
    assert completion == "Mocked completion"
    
    # Check that complete was called with the correct prompt
    mock_lm.complete.assert_called_once_with("Test prompt")


def test_get_default_model():
    """Test get_default_model function."""
    # Test with default environment
    model = get_default_model()
    assert isinstance(model, ModelManager)
    assert model.model_name == ModelManager.DEFAULT_MODEL
    
    # Test with custom environment
    with patch.dict(os.environ, {"CODEAGENT_MODEL": "custom/model"}):
        model = get_default_model()
        assert model.model_name == "custom/model"
