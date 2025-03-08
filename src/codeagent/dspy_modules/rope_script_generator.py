"""DSPy modules for code generation and modification."""

import os
import re
from typing import Optional

try:
    import dspy  # type: ignore

    DSPY_AVAILABLE = True
except ImportError:
    DSPY_AVAILABLE = False


# Simple assertion implementation since DSPy assertions are commented out in the installed version
class Assert:
    """Simple assertion implementation."""

    def __init__(self, condition, message, **_):
        """Initialize the assertion.

        Args:
            condition: The condition to check
            message: The error message if the condition is False
            **_: Additional arguments (ignored)
        """
        if not condition:
            raise ValueError(f"Assertion failed: {message}")


class RopeScriptGenerator:
    """Generate Python scripts that use the Rope library for code refactoring."""

    # List of valid Rope modules to import
    VALID_ROPE_MODULES = [
        "rope.base.project",
        "rope.base.exceptions",
        "rope.base.change",
        "rope.base.codeanalyze",
        "rope.base.evaluate",
        "rope.base.fscommands",
        "rope.base.history",
        "rope.base.libutils",
        "rope.base.prefs",
        "rope.base.pycore",
        "rope.base.pynamesdef",
        "rope.base.pynames",
        "rope.base.pyobjectsdef",
        "rope.base.pyobjects",
        "rope.base.pyscopes",
        "rope.base.resourceobserver",
        "rope.base.resources",
        "rope.base.simplify",
        "rope.base.stdmods",
        "rope.base.taskhandle",
        "rope.base.worder",
        "rope.refactor.extract",
        "rope.refactor.inline",
        "rope.refactor.introduce_factory",
        "rope.refactor.method_object",
        "rope.refactor.move",
        "rope.refactor.occurrences",
        "rope.refactor.rename",
        "rope.refactor.restructure",
        "rope.refactor.usefunction",
        "rope.refactor.change_signature",
        "rope.contrib.codeassist",
        "rope.contrib.findit",
    ]

    def __init__(self, model_name: Optional[str] = None):
        """Initialize the RopeScriptGenerator.

        Args:
            model_name: Optional model name to use for DSPy. If None, uses the
                model from environment variable CODEAGENT_MODEL or a default.
        """
        # Use the specified model name, or get it from environment, or use a default
        if model_name is None:
            model_name = os.environ.get("CODEAGENT_MODEL", "openrouter/google/gemini-2.0-flash-001")

        # Ensure DSPy is configured with the specified model
        if dspy.settings.lm is None:
            dspy.settings.configure(lm=dspy.LM(model_name))

        # Activate assertions for this module
        self.activate_assertions()

    def activate_assertions(self):
        """Activate assertions for this module."""
        try:
            from dspy.primitives.assertions import assert_transform_module  # type: ignore

            return assert_transform_module(self)
        except (ImportError, AttributeError):
            # If assertions are not available, return self
            return self

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

IMPORTANT: Only use the following Rope imports:
- from rope.base.project import Project
- from rope.base.exceptions import ...
- from rope.refactor.rename import Rename
- from rope.refactor.extract import ExtractMethod, ExtractVariable
- from rope.refactor.inline import Inline
- from rope.contrib.codeassist import get_definition_location

Example script structure:
```python
from rope.base.project import Project

def change_function(project_path, file_path):
    # Create a Rope project in the current directory
    project = Project(project_path)

    # Get the file resource
    source_code = project.get_resource(file_path)

    # Read the current content
    source = source_code.read()

    # Create the modified content
    new_source = "def modified_function():\\n    return 'Modified!'\\n"

    # Write the modified content back to the file
    source_code.write(new_source)

    # Return the modified content
    return new_source
```

Only output the Python code, nothing else.
"""

        response = dspy.settings.lm(prompt)

        # Extract the script from the response
        script = self._extract_script_from_response(response)
        return script

    def _extract_script_from_response(self, response):
        """Extract code from LLM response, handling different response formats."""
        # Handle list responses
        if isinstance(response, list):
            return response[0] if response else ""

        # Handle string responses
        if isinstance(response, str):
            # Extract code from markdown code blocks if present
            if "```python" in response and "```" in response.split("```python", 1)[1]:
                return response.split("```python", 1)[1].split("```", 1)[0].strip()
            elif "```" in response:
                return response.split("```", 1)[1].split("```", 1)[0].strip()
            return response

        # Handle other response types
        return str(response) if response else ""

    def _validate_script(self, script):
        """Validate the generated script using assertions."""
        try:
            # Check if the script contains the required function
            has_change_function = "def change_function(" in script
            Assert(has_change_function, "Script must define a 'change_function' function")

            # Check if the script has the correct function signature
            has_correct_signature = "def change_function(project_path, file_path):" in script
            Assert(
                has_correct_signature,
                "change_function must accept project_path and file_path parameters",
            )

            # Check if the script imports the required modules
            has_rope_import = "from rope.base.project import Project" in script
            Assert(has_rope_import, "Script must import 'Project' from 'rope.base.project'")

            # Check if the script creates a Rope project
            creates_project = "project = Project(project_path)" in script
            Assert(
                creates_project,
                "Script must create a Rope project using the project_path parameter",
            )

            # Check if the script gets the file resource
            gets_resource = "project.get_resource(file_path)" in script
            Assert(
                gets_resource,
                "Script must get the file resource using project.get_resource(file_path)",
            )

            # Check if the script returns the modified content
            returns_content = "return " in script
            Assert(returns_content, "Script must return the modified content")

            # Check for invalid imports
            import_regex = re.compile(r"from\s+(rope\.\S+)\s+import")
            for match in import_regex.finditer(script):
                module_name = match.group(1)
                if module_name not in self.VALID_ROPE_MODULES:
                    Assert(
                        False,
                        f"Invalid Rope module import: {module_name}. This module may not exist in the installed version of Rope.",
                    )

            # Check for syntax errors by attempting to compile the script
            compile(script, "<string>", "exec")

        except SyntaxError as e:
            # If there's a syntax error, raise a ValueError
            raise ValueError(f"Script has a syntax error: {str(e)}") from e
        except Exception as e:
            # If there's any other error, raise a ValueError
            raise ValueError(f"Script validation failed: {str(e)}") from e
