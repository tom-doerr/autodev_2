"""Tests for the cli module."""

import os
import tempfile
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from codeagent import cli


@pytest.fixture
def runner():
    """Create a CLI runner."""
    return CliRunner()


@pytest.fixture
def temp_file():
    """Create a temporary Python file."""
    with tempfile.NamedTemporaryFile(suffix=".py", delete=False) as temp:
        temp.write(b"def hello():\n    return 'Hello, World!'\n")
        temp_path = temp.name

    yield temp_path

    # Clean up
    if os.path.exists(temp_path):
        os.unlink(temp_path)


def test_cli_help(runner):  # pylint: disable=redefined-outer-name
    """Test the CLI help command."""
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "Codeagent CLI" in result.output


def test_modify_help(runner):  # pylint: disable=redefined-outer-name
    """Test the modify command help."""
    result = runner.invoke(cli, ["modify", "--help"])
    assert result.exit_code == 0
    assert "Modify a file based on instructions" in result.output


# Mock the entire CodeModifierAgent class
@patch("codeagent.cli.get_default_code_modifier")
def test_modify_command(
    mock_get_modifier, runner, temp_file
):  # pylint: disable=redefined-outer-name
    """Test the modify command."""
    # Create a mock code modifier that returns a fixed string
    mock_modifier = MagicMock()
    mock_modifier.modify_file.return_value = "def hello():\n    return 'Hello, Modified!'\n"
    mock_get_modifier.return_value = mock_modifier

    # Run the command in isolated filesystem to avoid modifying real files
    with runner.isolated_filesystem():
        # Copy the content to a file in the isolated filesystem
        with open(os.path.basename(temp_file), "w", encoding="utf-8") as f:
            f.write("def hello():\n    return 'Hello, World!'\n")

        # Run the command
        result = runner.invoke(cli, ["modify", os.path.basename(temp_file), "Change the greeting"])

        # Check the result
        assert result.exit_code == 0
        assert "File modified:" in result.output

        # Check that the modifier was called correctly
        mock_modifier.modify_file.assert_called_once_with(
            os.path.basename(temp_file), "Change the greeting"
        )


# Mock the entire CodeModifierAgent class
@patch("codeagent.cli.get_default_code_modifier")
def test_generate_command(mock_get_modifier, runner):  # pylint: disable=redefined-outer-name
    """Test the generate command."""
    # Create a mock code modifier that returns a fixed string
    mock_modifier = MagicMock()
    mock_modifier.generate_code.return_value = (
        "def factorial(n):\n    return 1 if n <= 1 else n * factorial(n-1)\n"
    )
    mock_get_modifier.return_value = mock_modifier

    # Run the command in isolated filesystem to avoid modifying real files
    with runner.isolated_filesystem():
        output_file = "factorial.py"

        # Run the command
        result = runner.invoke(cli, ["generate", "Create a factorial function", output_file])

        # Check the result
        assert result.exit_code == 0
        assert "Code generated:" in result.output

        # Check that the modifier was called correctly
        mock_modifier.generate_code.assert_called_once_with("Create a factorial function")

        # Check that the file was created with the generated code
        with open(output_file, "r", encoding="utf-8") as f:
            content = f.read()
        assert "def factorial" in content
