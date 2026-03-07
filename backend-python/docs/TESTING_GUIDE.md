# Testing Guide

## Setup

### 1. Install test dependencies
```bash
pip install pytest pytest-cov pytest-mock
```

### 2. Install project dependencies
```bash
pip install -r requirements.txt
```

## Running Tests

### Run all tests
```bash
pytest
```

### Run with coverage report
```bash
pytest --cov=. --cov-report=html
```
This generates a detailed coverage report in `htmlcov/index.html`.

### Run specific test file
```bash
pytest tests/test_classifiers.py
pytest tests/test_memory.py
pytest tests/test_db.py
pytest tests/test_graph.py
pytest tests/test_app.py
```

### Run specific test
```bash
pytest tests/test_classifiers.py::TestClassifyQuery::test_classify_greeting
```

### Run with verbose output
```bash
pytest -v
```

### Run tests matching pattern
```bash
pytest -k "test_memory"  # Run all tests with "test_memory" in name
pytest -k "not slow"     # Run all tests except those marked as slow
```

### Run tests in specific order
```bash
pytest --collect-only  # List all tests
```

## Test Structure

### Unit Tests
- `test_classifiers.py` - Classification logic (no API calls)
- `test_memory.py` - Memory extraction and compression
- `test_db.py` - Database helper functions
- `test_graph.py` - Graph nodes and routing

### Integration Tests
- `test_app.py` - FastAPI endpoints

## Mocking Strategy

All external dependencies are mocked:
- **LLM calls** - Mocked to return predetermined responses
- **Database** - Mocked MySQL service
- **Gmail API** - Not directly tested (handled by email_poller separately)

## Coverage Goals

- **Classifiers**: 85%+ coverage (pure functions, easy to test)
- **Memory**: 80%+ coverage (core logic)
- **Database**: 75%+ coverage (IO-heavy)
- **Graph**: 70%+ coverage (many node variations)
- **App**: 60%+ coverage (integration testing is harder)

## CI/CD Integration

For GitHub Actions:
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - run: pip install -r requirements.txt pytest pytest-cov
      - run: pytest --cov=. --cov-report=xml
      - uses: codecov/codecov-action@v2
```

## Debugging Failed Tests

### Print debug info
```bash
pytest -v -s  # -s shows print() statements
```

### Drop into debugger on failure
```bash
pytest --pdb  # Drops into pdb on failure
```

### Run with full traceback
```bash
pytest -v --tb=long
```

## Common Issues

**Issue**: Tests fail with "ModuleNotFoundError"
- **Solution**: Ensure you're in the project root directory when running pytest

**Issue**: Mock not working as expected
- **Solution**: Check that the import path in @patch matches where the object is used, not where it's defined

**Issue**: Test passes locally but fails in CI/CD
- **Solution**: Check for hardcoded paths, environment variables, or timezone-dependent assertions

## Adding New Tests

1. Create test file in `tests/` directory
2. Name it `test_*.py`
3. Create test class `Test*` or functions `test_*`
4. Use fixtures from `conftest.py`
5. Run `pytest` to verify

Example:
```python
# tests/test_new_feature.py
import pytest
from unittest.mock import Mock, patch

class TestNewFeature:
    def test_something(self, mock_llm):
        """Test description."""
        # Setup
        mock_llm.invoke.return_value = Mock(content="response")
        
        # Action
        result = some_function(mock_llm)
        
        # Assert
        assert result == expected_value
        mock_llm.invoke.assert_called_once()
```
