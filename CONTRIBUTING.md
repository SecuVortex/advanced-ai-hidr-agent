# Contributing to HIDR

Thank you for your interest in contributing to HIDR! This document provides guidelines for contributions.

## Code of Conduct

- Be respectful and inclusive
- Focus on defensive security only
- No malicious code or exploits
- Help others learn

## How to Contribute

### Reporting Bugs

1. Check if the bug is already reported in [Issues](https://github.com/yourusername/hidr-system/issues)
2. Create a new issue with:
   - Clear title and description
   - Steps to reproduce
   - Expected vs actual behavior
   - System information (OS, Python version)
   - Logs (if applicable)

### Suggesting Features

1. Open an issue with the `enhancement` label
2. Describe the feature and its use case
3. Explain how it improves defensive security

### Pull Requests

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass (`pytest tests/`)
6. Update documentation
7. Commit with clear messages
8. Push to your fork
9. Open a Pull Request

## Development Setup

```bash
# Clone your fork
git clone https://github.com/yourusername/hidr-system.git
cd hidr-system

# Install dependencies
pip install -r requirements.txt

# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html
```

## Coding Standards

- Follow PEP 8 style guide
- Add docstrings to all functions/classes
- Write unit tests for new features
- Keep functions focused and small
- Use meaningful variable names
- Comment complex logic

## Testing

- All new features must have tests
- Maintain 70%+ code coverage
- Test on Windows, Linux, and macOS (if possible)
- Include integration tests for major features

## Documentation

- Update README.md for user-facing changes
- Update CHANGELOG.md with your changes
- Add docstrings to new code
- Include usage examples

## Areas for Contribution

### High Priority
- Additional YARA rules
- New detection techniques
- Performance optimizations
- Cross-platform compatibility
- Documentation improvements

### Medium Priority
- GUI enhancements
- Additional export formats
- More test coverage
- Code refactoring

### Low Priority
- Visual improvements
- Additional examples
- Translations

## Questions?

- Open a discussion in [GitHub Discussions](https://github.com/yourusername/hidr-system/discussions)
- Email: secuvortex@gmail.com

Thank you for contributing to defensive cybersecurity! 🛡️
