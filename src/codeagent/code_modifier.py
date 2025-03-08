"""Code modification module for the CodeAgent."""

import importlib.util
import os
import tempfile
from typing import Optional

from codeagent.dspy_modules.rope_script_generator import RopeScriptGenerator


class CodeModifierAgent:
    """Agent for modifying code based on instructions using Rope."""

    def __init__(self, model_name: Optional[str] = None):
        """Initialize the code modifier agent."""
        self.model_name = model_name
        self.rope_script_generator = RopeScriptGenerator(model_name)

    def modify_file(self, file_path: str, instructions: str, project_path: Optional[str] = None):
        """Modify a file based on instructions using Rope.

        Args:
            file_path: Path to the file to modify.
            instructions: Instructions for modifying the file.
            project_path: Path to the project containing the file. If None, uses the directory
                containing the file.

        Returns:
            The modified code.

        Raises:
            ValueError: If the Rope script execution fails.
        """
        # Read the file content
        with open(file_path, "r", encoding="utf-8") as f:
            file_content = f.read()

        # Generate a Rope script to modify the file
        rope_script = self.rope_script_generator(file_content, instructions)

        # If no project path is provided, use the directory containing the file
        if project_path is None:
            project_path = os.path.dirname(os.path.abspath(file_path))

        # Execute the Rope script to modify the file
        return self._execute_rope_script(rope_script, project_path, file_path)

    def _execute_rope_script(self, script: str, project_path: str, file_path: str):
        """Execute a Rope script to modify code.

        Args:
            script: The Rope script to execute.
            project_path: Path to the project containing the file.
            file_path: Path to the file to modify.

        Returns:
            The modified code.

        Raises:
            ValueError: If the Rope script execution fails.
        """
        # Create a temporary file for the script
        fd, temp_file_path = tempfile.mkstemp(suffix=".py")
        os.close(fd)

        try:
            # Write the script to the temporary file
            with open(temp_file_path, "w", encoding="utf-8") as f:
                f.write(script)

            # Load the script as a module
            module = self._load_module_from_file(temp_file_path)

            # Get the relative path for Rope
            rel_file_path = self._get_relative_path(file_path, project_path)

            # Execute the Rope script
            return self._run_script_function(module, project_path, rel_file_path)
        except Exception as e:
            raise ValueError(f"Error executing Rope script from temporary file {temp_file_path}: {e}") from e
        finally:
            # Clean up the temporary file
            os.unlink(temp_file_path)

    def _load_module_from_file(self, file_path):
        """Load a Python module from a file.

        Args:
            file_path: Path to the Python file.

        Returns:
            The loaded module.

        Raises:
            ImportError: If the module could not be loaded.
        """
        spec = importlib.util.spec_from_file_location("rope_script", file_path)
        if spec is None:
            raise ImportError(f"Could not load module from {file_path}")

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def _get_relative_path(self, file_path, project_path):
        """Get the relative path of a file with respect to the project path.
        
        Uses pathlib for clarity. See [docs.python.org](https://docs.python.org/3/library/pathlib.html) and [docs.python.org](https://docs.python.org/3/library/os.path.html) for more details.
        
        Args:
            file_path: Path to the file.
            project_path: Path to the project.
        
        Returns:
            The relative path as a string.
        """
        from pathlib import Path
        try:
            rel_path = Path(file_path).relative_to(Path(project_path))
            return str(rel_path)
        except ValueError:
            return os.path.relpath(file_path, project_path)

    def _run_script_function(self, module, project_path, file_path):
        """Run the appropriate function from a Rope script module.

        Args:
            module: The loaded module.
            project_path: Path to the project.
            file_path: Path to the file (relative to project_path).

        Returns:
            The result of the function call.

        Raises:
            ValueError: If the module does not contain a suitable function.
        """
        if hasattr(module, "change_function"):
            return module.change_function(project_path, file_path)

        # Fallback to refactor_code for backward compatibility
        if hasattr(module, "refactor_code"):
            return module.refactor_code(project_path, file_path)

        raise ValueError("Rope script does not contain a change_function or refactor_code function")

    def generate_code(self, instructions: str):
        """Generate code based on instructions using Rope.

        Args:
            instructions: Instructions for generating the code.

        Returns:
            The generated code.

        Raises:
            ValueError: If the Rope script execution fails.
        """
        # Generate a Rope script to create the code
        rope_script = self.rope_script_generator("", f"Create a new file with: {instructions}")

        # Create a temporary directory to act as the project
        with tempfile.TemporaryDirectory() as project_path:
            # Create a temporary file path within the project
            temp_file_path = os.path.join(project_path, "generated_code.py")

            # Create an empty file
            with open(temp_file_path, "w", encoding="utf-8") as _:
                pass

            # Execute the Rope script to generate the code
            generated_code = self._execute_rope_script(rope_script, project_path, temp_file_path)

            return generated_code


def get_default_code_modifier() -> CodeModifierAgent:
    """Get the default code modifier agent."""
    model_name = os.environ.get("CODEAGENT_MODEL")
    return CodeModifierAgent(model_name)
