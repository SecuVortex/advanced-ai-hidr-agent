# Contributing to Multi-Agent HIDR System

Thank you for your interest in contributing to the Multi-Agent HIDR System! 🎉

## 🤝 How to Contribute

### Reporting Bugs

If you find a bug, please create an issue with:
- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- System information (OS, Python version)
- Relevant logs or error messages

### Suggesting Features

We welcome feature suggestions! Please create an issue with:
- Clear description of the feature
- Use case and benefits
- Proposed implementation (if applicable)

### Code Contributions

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**
   - Follow the code style guidelines
   - Add tests for new functionality
   - Update documentation

4. **Run tests**
   ```bash
   python -m pytest tests/
   ```

5. **Commit your changes**
   ```bash
   git commit -m "Add: Brief description of changes"
   ```

6. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Create a Pull Request**

## 📝 Code Style Guidelines

### Python Style

- Follow **PEP 8** guidelines
- Use **type hints** for function parameters and returns
- Write **docstrings** for all classes and functions (Google style)
- Maximum line length: **100 characters**

Example:

```python
def analyze_threat(
    threat_data: Dict[str, Any],
    threshold: int = 5
) -> Dict[str, Any]:
    """
    Analyze threat data and return results.
    
    Args:
        threat_data: Dictionary containing threat information
        threshold: Minimum threat level to flag (default: 5)
        
    Returns:
        Dictionary with analysis results
        
    Raises:
        ValueError: If threat_data is invalid
    """
    # Implementation
    pass
```

### Code Organization

- **One class per file** (except small helper classes)
- **Group related functions** together
- **Use meaningful names** for variables and functions
- **Avoid magic numbers** - use named constants

### Error Handling

```python
try:
    result = risky_operation()
except SpecificException as e:
    logger.error(f"Operation failed: {e}")
    return default_value
```

### Logging

```python
import logging

logger = logging.getLogger(__name__)

logger.info("Normal operation")
logger.warning("Suspicious activity detected")
logger.error("Operation failed")
```

## 🧪 Testing Guidelines

### Writing Tests

- Write tests for **all new functionality**
- Use **descriptive test names**
- Follow **AAA pattern** (Arrange, Act, Assert)
- Mock **external dependencies** (APIs, file system)

Example:

```python
def test_detection_agent_identifies_malware(self):
    """Test that DetectionAgent correctly identifies malware"""
    # Arrange
    agent = DetectionAgent()
    malware_data = {
        "name": "ransomware.exe",
        "path": "C:\\temp\\ransomware.exe"
    }
    
    # Act
    result = agent.analyze(malware_data)
    
    # Assert
    self.assertTrue(result["is_suspicious"])
    self.assertGreater(result["threat_level"], 5)
```

### Test Coverage

- Aim for **80%+ code coverage**
- Test **edge cases** and **error conditions**
- Test **integration** between components

## 📚 Documentation Guidelines

### Code Documentation

- **Docstrings** for all public classes and methods
- **Inline comments** for complex logic
- **Type hints** for better IDE support

### README Updates

- Update README.md for **new features**
- Add **usage examples** for new functionality
- Update **configuration** section if needed

### Architecture Documentation

- Update ARCHITECTURE.md for **structural changes**
- Document **design decisions**
- Add **diagrams** for complex workflows

## 🔒 Security Guidelines

### API Keys

- **Never commit** API keys or secrets
- Use **.env** file for configuration
- Add sensitive files to **.gitignore**

### Code Security

- **Validate all inputs**
- **Sanitize file paths**
- **Use parameterized queries** (if applicable)
- **Handle errors gracefully**

## 🎯 Development Areas

We especially welcome contributions in:

### 1. New Agents
- Implement specialized agents for specific threats
- Add agents for different security domains

### 2. New Tools
- Integrate additional threat intelligence sources
- Add new analysis capabilities
- Implement new response actions

### 3. Performance Optimization
- Improve workflow execution speed
- Optimize resource usage
- Add caching mechanisms

### 4. Testing
- Expand test coverage
- Add integration tests
- Create performance benchmarks

### 5. Documentation
- Improve user guides
- Add tutorials and examples
- Create video demonstrations

### 6. GUI Enhancements
- Improve user interface
- Add visualization features
- Implement real-time dashboards

## 🐛 Debugging Tips

### Enable Debug Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### View Agent Communication

```python
result = hidr.analyze_process(...)
hidr.print_agent_communication(result)
```

### Test Individual Agents

```python
from agents.detection_agent import DetectionAgent

agent = DetectionAgent()
result = agent.analyze_process("test.exe", "C:\\test.exe", "", 1234)
print(result)
```

## 📋 Pull Request Checklist

Before submitting a PR, ensure:

- [ ] Code follows style guidelines
- [ ] All tests pass
- [ ] New tests added for new functionality
- [ ] Documentation updated
- [ ] No API keys or secrets committed
- [ ] Commit messages are clear and descriptive
- [ ] PR description explains changes

## 🎓 Learning Resources

### LangGraph
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [Multi-Agent Systems Guide](https://python.langchain.com/docs/use_cases/agent_simulations/)

### Cybersecurity
- [MITRE ATT&CK Framework](https://attack.mitre.org/)
- [VirusTotal API Documentation](https://developers.virustotal.com/reference/overview)

### Python Best Practices
- [PEP 8 Style Guide](https://pep8.org/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)

## 💬 Communication

- **GitHub Issues** - Bug reports and feature requests
- **Pull Requests** - Code contributions
- **Discussions** - General questions and ideas

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

## 🙏 Thank You!

Your contributions make this project better for everyone. We appreciate your time and effort! ❤️

---

**Questions?** Feel free to open an issue or start a discussion!
