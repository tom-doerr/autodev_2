import subprocess
import pytest

def test_ruff_lint():
    """
    Run Ruff linter via pytest and show linting issues.

    This test is based on guidance from [stackoverflow.com](https://stackoverflow.com/questions/77498238/vs-code-you-have-deprecated-linting-or-formatting-settings-for-python)
    and [reddit.com](https://www.reddit.com/r/vscode/comments/140t4of/linting_issues_for_python/) to ensure linting errors are always reported during test runs.
    """
    result = subprocess.run(["ruff", "check", "."], capture_output=True, text=True)
    if result.returncode != 0:
        print("Ruff linting issues found:")
        print(result.stdout)
        print(result.stderr)
        pytest.fail(f"Ruff linting failed with exit code {result.returncode}")
