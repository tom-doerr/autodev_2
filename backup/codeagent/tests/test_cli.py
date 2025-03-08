"""Tests for the cli module."""

import os
import tempfile
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from codeagent.cli import cli, modify


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


def test_cli_help(runner):
    """Test the CLI help command."""
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "CodeAgent: A minimal coding agent" in result.output


def test_modify_help(runner):
    """Test the modify command help."""
    result = runner.invoke(cli, ["modify", "--help"])
    assert result.exit_code == 0
    assert "Modify a file based on the given instruction" in result.output


def test_modify_missing_file(runner):
    """Test the modify command with a missing file."""
    result = runner.invoke(cli, [
        "modify",
        "--file", "nonexistent.py",
        "--instruction", "Add error handling"
    ])
    assert result.exit_code == 1
    assert "Error: File not found" in result.output


def test_modify_file_stdout(runner, temp_file):
    """Test the modify command with output to stdout."""
    with patch("codeagent.cli.CodeModifier") as MockCodeModifier:
        mock_instance = MagicMock()
        mock_instance.modify_file.return_value = "Modified content"
        MockCodeModifier.return_value = mock_instance
        
        result = runner.invoke(cli, [
            "modify",
            "--file", temp_file,
            "--instruction", "Add error handling"
        ])
        
        assert result.exit_code == 0
        assert "Modified content" in result.output
        
        # Check that the modifier was called with the correct arguments
        mock_instance.load_project.assert_called_once()
        mock_instance.modify_file.assert_called_once_with(
            os.path.abspath(temp_file),
            "Add error handling"
        )


def test_modify_file_output(runner, temp_file):
    """Test the modify command with output to a file."""
    with tempfile.NamedTemporaryFile(suffix=".py", delete=False) as output_file:
        output_path = output_file.name
    
    try:
        with patch("codeagent.cli.CodeModifier") as MockCodeModifier:
            mock_instance = MagicMock()
            mock_instance.modify_file.return_value = "Modified content"
            MockCodeModifier.return_value = mock_instance
            
            result = runner.invoke(cli, [
                "modify",
                "--file", temp_file,
                "--instruction", "Add error handling",
                "--output", output_path
            ])
            
            assert result.exit_code == 0
            assert f"Modified file saved to: {output_path}" in result.output
            
            # Check that the output file contains the modified content
            with open(output_path, "r") as f:
                content = f.read()
                assert content == "Modified content"
    finally:
        # Clean up
        if os.path.exists(output_path):
            os.unlink(output_path)


def test_modify_with_project(runner, temp_file):
    """Test the modify command with a specified project path."""
    with tempfile.TemporaryDirectory() as project_dir:
        with patch("codeagent.cli.CodeModifier") as MockCodeModifier:
            mock_instance = MagicMock()
            MockCodeModifier.return_value = mock_instance
            
            result = runner.invoke(cli, [
                "modify",
                "--file", temp_file,
                "--instruction", "Add error handling",
                "--project", project_dir
            ])
            
            assert result.exit_code == 0
            
            # Check that the project was loaded with the correct path
            mock_instance.load_project.assert_called_once_with(os.path.abspath(project_dir))


def test_modify_error(runner, temp_file):
    """Test the modify command when an error occurs."""
    with patch("codeagent.cli.CodeModifier") as MockCodeModifier:
        mock_instance = MagicMock()
        mock_instance.modify_file.side_effect = Exception("Test error")
        MockCodeModifier.return_value = mock_instance
        
        result = runner.invoke(cli, [
            "modify",
            "--file", temp_file,
            "--instruction", "Add error handling"
        ])
        
        assert result.exit_code == 1
        assert "Error: Test error" in result.output
