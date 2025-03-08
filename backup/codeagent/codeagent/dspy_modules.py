"""DSPy modules for code generation and modification."""

import os
from typing import Optional

try:
    import dspy
    DSPY_AVAILABLE = True
except ImportError:
    DSPY_AVAILABLE = False


class RopeScriptGenerator:
    """Generate Rope scripts for code modification."""
    
    def __init__(self, model_name: Optional[str] = None):
        """Initialize the Rope script generator."""
        self.model_name = model_name
        from codeagent.dspy_config import configure_dspy, DSPY_AVAILABLE
        # Set up the language model if DSPy is available
        if DSPY_AVAILABLE:
            if model_name:
                self.lm = configure_dspy(model_name)
            elif not hasattr(dspy.settings, 'lm') or not dspy.settings.lm:
                default_model = os.environ.get("CODEAGENT_MODEL", "openrouter/google/gemini-2.0-flash-001")
                self.lm = configure_dspy(default_model)
            else:
                self.lm = dspy.settings.lm
    
    def __call__(self, code: str, instructions: str) -> str:
        """Generate a Rope script to modify the given code."""
        if not DSPY_AVAILABLE:
            raise ImportError("DSPy is required for RopeScriptGenerator")
        
        # Make sure we have a language model
        assert dspy.settings.lm is not None, "No language model configured"
        
        # Generate the Rope script using the LM directly
        prompt = f"""
You are an expert Python programmer. Your task is to write a Python script that uses the Rope library to modify code according to the given instructions.

The script should define a function called 'refactor_code' that takes two parameters:
1. project_path: The path to the project root
2. file_path: The relative path to the file to modify

The function should use Rope to modify the file according to the instructions and return the modified content.

Here are the instructions for modifying the code:
{instructions}

Here is the code to modify:
```python
{code}
```

Write a Python script that uses Rope to implement these changes. The script should be self-contained and not rely on any external dependencies other than Rope.
"""
        
        response = dspy.settings.lm(prompt=prompt)
        
        # Extract the script from the response
        if isinstance(response, list):
            script = response[0] if response else ""
        else:
            script = response
        
        # If the script is wrapped in markdown code blocks, extract just the code
        if isinstance(script, str):
            if "```python" in script and "```" in script.split("```python", 1)[1]:
                script = script.split("```python", 1)[1].split("```", 1)[0].strip()
            elif "```" in script:
                script = script.split("```", 1)[1].split("```", 1)[0].strip()
        
        return script
