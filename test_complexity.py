"""Test file to demonstrate cyclomatic complexity checking."""

def simple_function(value):
    """A simple function with low complexity."""
    return value * 2

def complex_function(value):
    """A function with high cyclomatic complexity (>5)."""
    if value < 0:
        return -1
    if value == 0:
        return 0
    if value < 10:
        return 1
    if value < 20:
        return 2
    if value < 30:
        return 3
    if value < 40:
        return 4
    if value < 50:
        return 5
    return 6

def test_simple_function():
    """Test the simple function."""
    assert simple_function(2) == 4

def test_complex_function():
    """Test the complex function."""
    assert complex_function(-5) == -1
    assert complex_function(0) == 0
    assert complex_function(5) == 1
    assert complex_function(15) == 2
    assert complex_function(25) == 3
    assert complex_function(35) == 4
    assert complex_function(45) == 5
    assert complex_function(55) == 6
