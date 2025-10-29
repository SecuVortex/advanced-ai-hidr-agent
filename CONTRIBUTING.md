# Contributing to HIDR

Thank you for your interest in contributing to HIDR!

## How to Contribute

### Reporting Bugs
- Use the bug report template
- Include OS, Python version, and HIDR version
- Provide logs and steps to reproduce

### Suggesting Features
- Use the feature request template
- Explain the use case clearly
- Consider security implications

### Code Contributions

1. **Fork the repository**
2. **Create a branch**: `git checkout -b feature/your-feature`
3. **Make changes**:
   - Follow existing code style
   - Add tests for new features
   - Update documentation
4. **Test**: `pytest tests/ -v`
5. **Commit**: `git commit -m "Add: your feature"`
6. **Push**: `git push origin feature/your-feature`
7. **Create Pull Request**

## Code Standards

- Python 3.8+ compatibility
- PEP 8 style guide
- Type hints where applicable
- Docstrings for functions/classes
- Unit tests for new code (aim for 75%+ coverage)

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html
```

## Security

- Never commit API keys or credentials
- Use `.env.example` for environment variables
- Report security issues privately to secuvortex@gmail.com

## Questions?

Contact: secuvortex@gmail.com

---

**Built with ❤️ for Defensive Cybersecurity**
