import pytest

def run_tests():
    """Run pytest tests and return the results."""
    result = pytest.main(["tests"])
    return result
