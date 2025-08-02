# Contributing to AutoPromptix

Thank you for your interest in contributing to AutoPromptix! This document provides guidelines and information for contributors to help make the contribution process smooth and effective.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Contributing Guidelines](#contributing-guidelines)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Documentation](#documentation)
- [Issue Reporting](#issue-reporting)
- [Community](#community)

## Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct. We are committed to providing a welcoming and inclusive environment for all contributors.

### Our Standards

- **Be respectful**: Treat all community members with respect and kindness
- **Be inclusive**: Welcome newcomers and help them get started
- **Be collaborative**: Work together towards common goals
- **Be constructive**: Provide helpful feedback and suggestions
- **Be patient**: Understand that people have different skill levels and backgrounds

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Node.js 16 or higher (for dashboard frontend)
- Git for version control
- A GitHub account

### Project Structure

```
autopromptix/
├── autopromptix/           # Core library
│   ├── decorators.py       # Test decorators
│   ├── storage.py          # Storage management
│   ├── prompt_improver.py  # AI prompt optimization
│   ├── test_runner.py      # Test execution
│   └── test_data_pool.py   # Test data management
├── dashboard/              # Web dashboard
│   ├── backend/            # Flask API server
│   ├── frontend/           # React + TypeScript UI
│   └── requirements.txt    # Dashboard dependencies
├── examples/               # Usage examples
├── tests/                  # Test suite
├── docs/                   # Documentation
└── requirements.txt        # Core dependencies
```

## Development Setup

### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then clone your fork
git clone https://github.com/YOUR_USERNAME/autopromptix.git
cd autopromptix

# Add upstream remote
git remote add upstream https://github.com/dogfoot-brothers/autopromptix.git
```

### 2. Set up Python Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r dashboard/requirements.txt

# Install in development mode
pip install -e .
```

### 3. Set up Dashboard Frontend (Optional)

```bash
cd dashboard/frontend
npm install
# or with yarn
yarn install
```

### 4. Verify Installation

```bash
# Run tests
python -m pytest tests/

# Start dashboard backend
cd dashboard/backend
python server.py

# Start dashboard frontend (in another terminal)
cd dashboard/frontend
npm run dev
```

## Contributing Guidelines

### Types of Contributions

We welcome various types of contributions:

- **Bug fixes**: Fix existing issues
- **New features**: Add new functionality
- **Documentation**: Improve or add documentation
- **Tests**: Add or improve test coverage
- **Examples**: Provide usage examples
- **Performance**: Optimize existing code
- **Refactoring**: Improve code structure

### Before You Start

1. **Check existing issues**: Look for existing issues related to your contribution
2. **Create an issue**: For new features or significant changes, create an issue first to discuss
3. **Small changes**: For small bug fixes or documentation updates, you can directly create a PR

### Branch Naming Convention

Use descriptive branch names with prefixes:

- `feature/your-feature-name` - New features
- `fix/issue-description` - Bug fixes
- `docs/documentation-update` - Documentation changes
- `test/test-improvement` - Test additions/improvements
- `refactor/code-improvement` - Refactoring

Examples:
- `feature/async-test-runner`
- `fix/storage-memory-leak`
- `docs/api-reference-update`

## Pull Request Process

### 1. Prepare Your Changes

```bash
# Create a new branch
git checkout -b feature/your-feature-name

# Make your changes
# ... edit files ...

# Add and commit changes
git add .
git commit -m "Add feature: your feature description"

# Push to your fork
git push origin feature/your-feature-name
```

### 2. Create Pull Request

1. Go to your fork on GitHub
2. Click "New Pull Request"
3. Select the base branch (usually `dev`)
4. Fill out the PR template (see PULL_REQUEST_TEMPLATE.md)
5. Submit the pull request

### 3. PR Requirements

- **Clear description**: Explain what your changes do and why
- **Issue reference**: Link to related issues
- **Tests**: Include tests for new functionality
- **Documentation**: Update documentation if needed
- **Code quality**: Follow coding standards
- **Small commits**: Keep commits focused and atomic

### 4. Review Process

1. **Automated checks**: Ensure all CI checks pass
2. **Code review**: Maintainers will review your code
3. **Address feedback**: Make requested changes
4. **Approval**: PR will be approved and merged

## Coding Standards

### Python Code Style

We follow PEP 8 with some modifications:

```python
# Use type hints
def process_test_data(data: Dict[str, Any]) -> TestResult:
    """Process test data and return result."""
    pass

# Use descriptive variable names
test_results = []
function_metadata = get_function_metadata(func)

# Use docstrings for classes and functions
class TestRunner:
    """Runs tests for AI functions with prompt optimization."""
    
    def run_test(self, function: callable, test_case: TestCase) -> TestResult:
        """Run a single test case against the function.
        
        Args:
            function: The function to test
            test_case: Test case data
            
        Returns:
            Test result with success/failure status
        """
        pass
```

### Frontend Code Style

For React/TypeScript frontend:

```typescript
// Use functional components with hooks
const Dashboard: React.FC = () => {
  const [loading, setLoading] = useState(false)
  
  return <div>Dashboard content</div>
}

// Use proper TypeScript interfaces
interface TestPoolData {
  name: string
  description: string
  test_cases: TestCase[]
}

// Use meaningful component names
export default Dashboard
```

### File Formatting

- **Always end files with a newline character**
- Use consistent indentation (4 spaces for Python, 2 spaces for JavaScript/TypeScript)
- Remove trailing whitespace
- Use meaningful file and variable names

## Testing

### Writing Tests

```python
# Test file example: tests/test_decorators.py
import pytest
from autopromptix.decorators import test

def test_decorator_registration():
    """Test that @test decorator properly registers functions."""
    
    @test(description="Sample test function")
    def sample_function(input_text: str) -> str:
        return f"Processed: {input_text}"
    
    # Test assertions
    assert sample_function("test") == "Processed: test"
    # Add more assertions...

def test_error_handling():
    """Test error handling in decorators."""
    # Test error scenarios
    pass
```

### Running Tests

```bash
# Run all tests
python -m pytest

# Run specific test file
python -m pytest tests/test_decorators.py

# Run with coverage
python -m pytest --cov=autopromptix

# Run frontend tests
cd dashboard/frontend
npm test
```

### Test Coverage

- Maintain at least 80% test coverage
- Add tests for new features
- Test both success and error scenarios
- Include integration tests where appropriate

## Documentation

### API Documentation

Use clear docstrings with examples:

```python
def create_test_pool(name: str, description: str, test_cases: List[TestCase]) -> TestDataPool:
    """Create a new test data pool.
    
    Args:
        name: Unique name for the test pool
        description: Human-readable description
        test_cases: List of test cases to include
        
    Returns:
        Created test data pool instance
        
    Raises:
        ValueError: If name is empty or already exists
        
    Example:
        >>> pool = create_test_pool(
        ...     name="math_tests",
        ...     description="Basic math operations",
        ...     test_cases=[TestCase("2+2", "4", "addition")]
        ... )
        >>> pool.name
        'math_tests'
    """
```

### README Updates

Keep the main README.md updated with:
- New features and their usage
- Updated installation instructions
- New examples
- Breaking changes

## Issue Reporting

### Bug Reports

When reporting bugs, include:

1. **Clear title**: Descriptive summary of the issue
2. **Environment**: Python version, OS, package versions
3. **Steps to reproduce**: Detailed steps to recreate the bug
4. **Expected behavior**: What should happen
5. **Actual behavior**: What actually happens
6. **Code samples**: Minimal reproducible example
7. **Error messages**: Full error traceback if applicable

### Feature Requests

For feature requests, include:

1. **Use case**: Why is this feature needed?
2. **Proposed solution**: How should it work?
3. **Alternatives**: Other ways to achieve the same goal
4. **Implementation ideas**: Technical approach (if you have one)

## Community

### Communication Channels

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General questions and ideas
- **Pull Requests**: Code contributions and reviews

### Getting Help

1. **Check documentation**: Look at README and docs/ folder
2. **Search issues**: Check if your question was already asked
3. **Create an issue**: For bugs or feature requests
4. **Join discussions**: For general questions

### Recognition

Contributors will be recognized in:
- CONTRIBUTORS.md file
- Release notes for significant contributions
- GitHub contributors section

## Release Process

### Versioning

We use [Semantic Versioning](https://semver.org/):
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Workflow

1. Features are merged into `dev` branch
2. When ready for release, `dev` is merged into `main`
3. Version is tagged and release notes are created
4. Package is published to PyPI

## Thank You

Thank you for contributing to AutoPromptix! Your contributions help make AI function testing and improvement more accessible to everyone.

For questions about contributing, feel free to create an issue or reach out to the maintainers.

---

**Happy Coding!** 🚀