"""Test the import logic in model.py."""

import sys
from unittest.mock import MagicMock, patch

# Mock the dspy module to simulate both import scenarios
with patch.dict(sys.modules, {'dspy': None}):
    # This will force the import to fail
    from codeagent.model import DSPY_AVAILABLE as DSPY_UNAVAILABLE

# Test that DSPY_AVAILABLE is False when dspy is not available
assert DSPY_UNAVAILABLE is False

# Now mock dspy as available
mock_dspy = MagicMock()
with patch.dict(sys.modules, {'dspy': mock_dspy}):
    # Reload the module to get the updated DSPY_AVAILABLE value
    import importlib
    import codeagent.model
    importlib.reload(codeagent.model)
    from codeagent.model import DSPY_AVAILABLE as DSPY_AVAILABLE_MOCK

# Test that DSPY_AVAILABLE is True when dspy is available
assert DSPY_AVAILABLE_MOCK is True

print("All tests passed!")
