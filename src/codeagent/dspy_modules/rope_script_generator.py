"""Module for generating Rope scripts using DSPy."""

import os
import re

import dspy  # type: ignore


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

    def __init__(self, model_name=None):
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

    def __call__(self, file_content, instructions):
        """Generate a Python script that uses Rope to refactor the given file content.

        Args:
            file_content: The content of the file to refactor.
            instructions: Natural language instructions for the refactoring.

        Returns:
            A Python script that uses Rope to refactor the file.
        """
        # Check if this is a request to create a new file
        if not file_content and instructions.startswith("Create a new file with:"):
            return self._generate_new_file_script(
                instructions[len("Create a new file with:") :].strip()
            )

        # Otherwise, generate a refactoring script
        return self._generate_refactoring_script(file_content, instructions)

    def _generate_refactoring_script(self, file_content, instructions):
        """Generate a script for refactoring existing code."""
        # Create a prompt for the model
        prompt = f"""
You are a Python code refactoring expert. Your task is to write a Python script that uses the Rope library to refactor code.

Here are the instructions for the refactoring:
{instructions}

Here is the code to refactor:
```python
{file_content}
```

Write a Python script that uses the Rope library to perform this refactoring. The script should:
1. Define a function named `change_function(project_path, file_path)` that performs the refactoring.
2. Use the Rope library to perform the refactoring.
3. Return the modified code as a string.

The script should be self-contained and handle any necessary imports.

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

        # Generate the script using DSPy
        script = dspy.settings.lm(prompt)

        # Ensure the result is a string
        if isinstance(script, list):
            script = "\n".join(script)
        elif not isinstance(script, str):
            script = str(script)

        # Clean up the script
        script = self._clean_script(script)

        # Validate the script
        self._validate_script(script)

        return script

    def _generate_new_file_script(self, instructions):
        """Generate a script for creating a new file with code."""
        # Create a prompt for the model
        prompt = f"""
You are a Python code generation expert. Your task is to write a Python script that uses the Rope library to create a new file with code.

Here are the instructions for the code to generate:
{instructions}

Write a Python script that uses the Rope library to create this code. The script should:
1. Define a function named `change_function(project_path, file_path)` that creates the file with the requested code.
2. Use the Rope library to create or modify the file with the requested code.
3. Return the generated code as a string.

The script should be self-contained and handle any necessary imports.

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
    
    # Get or create the file resource
    source_code = project.get_resource(file_path)
    
    # Create the content for the new file
    new_source = "def new_function():\\n    return 'Hello, World!'\\n"
    
    # Write the content to the file
    source_code.write(new_source)
    
    # Return the generated content
    return new_source
```

Only output the Python code, nothing else.
"""

        # Generate the script using DSPy
        script = dspy.settings.lm(prompt)

        # Ensure the result is a string
        if isinstance(script, list):
            script = "\n".join(script)
        elif not isinstance(script, str):
            script = str(script)

        # Clean up the script
        script = self._clean_script(script)

        # Validate the script
        self._validate_script(script)

        return script

    def _clean_script(self, script):
        """Clean up the script by removing markdown code blocks and other artifacts."""
        # Remove markdown code blocks
        script = re.sub(r"```python\s*", "", script)
        script = re.sub(r"```\s*", "", script)

        # Remove any leading/trailing whitespace
        script = script.strip()

        return script

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
