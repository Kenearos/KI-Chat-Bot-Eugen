# Test Suite for Eugen Twitch Bot

Comprehensive test coverage for the Eugen bot components.

## Test Coverage

**Overall: 97% code coverage**

### Components Tested

- **MentionDetector** (utils.py) - 98% coverage
  - Explicit mentions (@Eugen, Eugen:, etc.)
  - Nickname detection and generation
  - Ambiguous greeting detection
  - Content extraction
  - Edge cases and unicode support

- **Logger** (utils.py) - 98% coverage
  - File-based logging
  - Log levels (INFO, DEBUG, ERROR, WARNING)
  - API call logging
  - Unicode character support

- **ConversationMemory** (memory.py) - 91% coverage
  - User history storage and retrieval
  - Time-based message filtering
  - Message limits enforcement
  - JSON persistence
  - Error handling

- **PerplexityProvider** (ai_provider.py) - 100% coverage
  - API request/response handling
  - Error handling (timeouts, network errors, HTTP errors)
  - Statistics tracking
  - API key validation

- **Config** (config.py) - 100% coverage
  - Environment variable loading
  - JSON configuration
  - Validation
  - Default values

## Running Tests

### Run all tests
```bash
pytest tests/
```

### Run with coverage report
```bash
pytest tests/ --cov=. --cov-report=term-missing
```

### Run specific test file
```bash
pytest tests/test_utils.py
pytest tests/test_memory.py
pytest tests/test_ai_provider.py
pytest tests/test_config.py
```

### Run specific test
```bash
pytest tests/test_utils.py::TestMentionDetector::test_mention_with_at_symbol
```

## Test Structure

```
tests/
├── __init__.py              # Package marker
├── conftest.py              # Shared fixtures and test configuration
├── test_utils.py            # Tests for MentionDetector and Logger
├── test_memory.py           # Tests for ConversationMemory
├── test_ai_provider.py      # Tests for PerplexityProvider
└── test_config.py           # Tests for Config
```

## Key Features

- **Test Isolation**: Each test runs in a clean environment with:
  - Isolated environment variables
  - Clean logging handlers
  - Temporary directories for file operations

- **Async Testing**: Full support for async/await with pytest-asyncio

- **Mocking**: HTTP requests mocked using pytest-mock to avoid real API calls

- **Fixtures**: Reusable test data in conftest.py:
  - `temp_dir`: Temporary directory with automatic cleanup
  - `mock_env_file`: Sample .env file
  - `mock_config_json`: Sample config.json
  - `sample_conversation_history`: Test chat history
  - `mock_perplexity_response`: Sample API response

## Test Statistics

- **Total Tests**: 116
- **Passing**: 116 (100%)
- **Code Coverage**: 97%
- **Test Execution Time**: ~1.2 seconds

## Coverage Gaps

The 3% uncovered code consists of:
- Error handling edge cases in memory.py (lines 92-94, 111-112, 143-144)
- Rarely-used utility functions in utils.py (lines 101, 165)

These are defensive code paths that are difficult to trigger in tests.
