---
applyTo: "**/*.py"
---
# Python Development Guidelines

Apply the [general coding guidelines](./copilot-instructions-general.md) to all code.

## Python Specific Guidelines

### Code Style
- Follow PEP 8 style guidelines
- Use Black for code formatting
- Maximum line length: 88 characters
- Use type hints for all function signatures
- Write docstrings for all public functions and classes

### Project Structure
```
project/
├── src/                 # Source code
│   └── package_name/
├── tests/              # Test files
├── docs/               # Documentation
├── requirements.txt    # Dependencies
├── pyproject.toml     # Project configuration
└── README.md          # Project description
```

### Import Organization
```python
# Standard library imports
import os
import sys
from typing import Dict, List, Optional

# Third-party imports
import requests
from flask import Flask, request

# Local application imports
from .models import User
from .utils import helper_function
```

### Type Hints
```python
from typing import Dict, List, Optional, Union

def process_data(
    data: List[Dict[str, str]], 
    filter_key: Optional[str] = None
) -> Dict[str, int]:
    """Process and count data entries."""
    pass
```

### Error Handling
- Use specific exception types
- Implement proper logging
- Add context to error messages
- Use try-except blocks judiciously

```python
import logging

logger = logging.getLogger(__name__)

try:
    result = risky_operation()
except SpecificError as e:
    logger.error(f"Operation failed: {e}")
    raise ProcessingError(f"Failed to process data: {e}") from e
```

### Documentation
- Use Google-style docstrings
- Include examples in docstrings
- Document complex algorithms
- Maintain README with setup instructions

```python
def calculate_score(
    values: List[float], 
    weights: Optional[List[float]] = None
) -> float:
    """Calculate weighted score from values.
    
    Args:
        values: List of numeric values to score
        weights: Optional weights for each value. If None, equal weights used.
        
    Returns:
        Calculated weighted score as float
        
    Raises:
        ValueError: If values and weights have different lengths
        
    Example:
        >>> calculate_score([1.0, 2.0, 3.0], [0.5, 0.3, 0.2])
        1.7
    """
    pass
```

### Testing
- Use pytest for testing
- Aim for >90% code coverage
- Write both unit and integration tests
- Use fixtures for test data

```python
import pytest
from unittest.mock import Mock, patch

@pytest.fixture
def sample_data():
    return {"key": "value", "number": 42}

def test_function_with_mock(sample_data):
    with patch('module.external_call') as mock_call:
        mock_call.return_value = "mocked"
        result = function_under_test(sample_data)
        assert result == expected_result
```

### Performance Guidelines
- Use list comprehensions and generator expressions
- Leverage built-in functions (map, filter, reduce)
- Profile code for bottlenecks
- Use appropriate data structures

### Security Best Practices
- Validate all user inputs
- Use parameterized queries for databases
- Don't hardcode secrets in code
- Implement proper authentication/authorization

### Dependency Management
- Pin dependency versions in requirements.txt
- Use virtual environments
- Separate dev and production dependencies
- Regular security updates

## Common Patterns

### Configuration Management
```python
import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class Config:
    api_key: str
    debug: bool = False
    timeout: int = 30
    
    @classmethod
    def from_env(cls) -> 'Config':
        return cls(
            api_key=os.getenv('API_KEY', ''),
            debug=os.getenv('DEBUG', 'false').lower() == 'true',
            timeout=int(os.getenv('TIMEOUT', '30'))
        )
```

### Data Validation
```python
from pydantic import BaseModel, validator

class UserData(BaseModel):
    name: str
    email: str
    age: int
    
    @validator('email')
    def validate_email(cls, v):
        if '@' not in v:
            raise ValueError('Invalid email format')
        return v
        
    @validator('age')
    def validate_age(cls, v):
        if v < 0 or v > 150:
            raise ValueError('Age must be between 0 and 150')
        return v
```

### Async Programming
```python
import asyncio
import aiohttp
from typing import List

async def fetch_data(session: aiohttp.ClientSession, url: str) -> dict:
    async with session.get(url) as response:
        return await response.json()

async def fetch_multiple(urls: List[str]) -> List[dict]:
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_data(session, url) for url in urls]
        return await asyncio.gather(*tasks)
```
