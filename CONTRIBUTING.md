# Contributing Guide

## How to Contribute

We welcome contributions! Please follow these guidelines:

### 1. Fork the Repository

```bash
git clone https://github.com/yourusername/ai-bot-platform.git
cd ai-bot-platform
```

### 2. Create Feature Branch

```bash
git checkout -b feature/your-feature-name
```

### 3. Install Development Dependencies

```bash
pip install -e ".[dev]"
```

### 4. Make Changes

- Follow PEP 8 style guide
- Write clear commit messages
- Add tests for new features
- Update documentation

### 5. Format Code

```bash
black src tests
isort src tests
```

### 6. Run Tests

```bash
pytest tests/ -v --cov=src
```

### 7. Commit Changes

```bash
git add .
git commit -m "Add: description of your changes"
git push origin feature/your-feature-name
```

### 8. Create Pull Request

- Describe your changes
- Reference any related issues
- Wait for code review

## Code Standards

### Python Style

- Line length: 120 characters
- Use type hints
- Document functions with docstrings
- Follow SOLID principles

### Naming Conventions

- Classes: `PascalCase`
- Functions: `snake_case`
- Constants: `UPPER_SNAKE_CASE`
- Private: `_leading_underscore`

### Type Hints

```python
async def send_message(
    user_id: str,
    content: str,
    message_type: str = "text",
) -> MessageResponse:
    """Send a message."""
    pass
```

### Documentation

```python
"""Module description."""

class MyClass:
    """Class description."""
    
    async def my_method(self, param: str) -> str:
        """
        Method description.
        
        Args:
            param: Parameter description
            
        Returns:
            Return value description
            
        Raises:
            ValueError: When something is wrong
        """
        pass
```

## Testing Requirements

- **Unit Tests**: For individual functions
- **Integration Tests**: For API endpoints
- **Target**: 90% code coverage

```python
import pytest

@pytest.mark.asyncio
async def test_my_function():
    """Test my function."""
    result = await my_function()
    assert result is not None
```

## Commit Message Format

```
<type>: <description>

<body>

<footer>
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

Examples:
- `feat: add user memory storage`
- `fix: resolve telegram webhook issue`
- `docs: update API documentation`

## Pull Request Process

1. Update documentation
2. Add tests for new features
3. Ensure all tests pass
4. Update CHANGELOG if needed
5. Request review from maintainers

## Issues

### Reporting Bugs

```
Title: [Bug] Brief description

Description:
- What did you do?
- What did you expect?
- What actually happened?

Environment:
- OS: Linux/Mac/Windows
- Python: 3.12.x
- Version: 1.0.0
```

### Feature Requests

```
Title: [Feature] Brief description

Description:
- What problem does this solve?
- How should it work?
- Any alternatives?
```

## Development Workflow

### 1. Local Development

```bash
docker-compose up -d
uvicorn src.main:app --reload
```

### 2. Run Tests

```bash
pytest tests/ -v --cov=src
```

### 3. Check Code Quality

```bash
black --check src tests
isort --check-only src tests
flake8 src tests
mypy src
```

### 4. Build Docker Image

```bash
docker build -t ai-bot:dev -f docker/Dockerfile .
```

## Release Process

1. Bump version in `pyproject.toml`
2. Update CHANGELOG
3. Create release tag
4. Push to main
5. GitHub Actions will build and push to Docker Hub

## Support

- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/yourusername/ai-bot-platform/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/ai-bot-platform/discussions)

## Code of Conduct

- Be respectful and inclusive
- No harassment or discrimination
- Constructive feedback only
- Report violations to team

---

Thank you for contributing to AI Bot Platform! 🚀
