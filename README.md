# pdfparse

A Python package for parsing PDF documents.

## Installation

```bash
pip install pdfparse
```

### Development Installation

For development, clone the repository and install in editable mode with development dependencies:

```bash
git clone https://github.com/willmorejg/pdfparse.git
cd pdfparse
pip install -e ".[dev]"
```

## Quick Start

### Command Line Usage

```bash
# Parse a PDF file
pdfparse document.pdf

# Parse with specific options
pdfparse document.pdf --output text --format json
```

### Python API

```python
import pdfparse

# Parse a PDF file
result = pdfparse.parse("document.pdf")
print(result.text)

# Parse with custom options
parser = pdfparse.Parser(extract_images=True)
result = parser.parse("document.pdf")
```

## Features

- Extract text from PDF documents
- Command line interface for batch processing
- Python API for programmatic access
- Support for various PDF formats
- Extensible plugin system

## Requirements

- Python 3.8+
- See `pyproject.toml` for full dependency list

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/willmorejg/pdfparse.git
cd pdfparse

# Install development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=pdfparse

# Run specific test file
pytest tests/test_parser.py
```

### Code Quality

This project uses several tools to maintain code quality:

```bash
# Format code
black src/ tests/

# Remove unused imports
autoflake --remove-all-unused-imports --recursive src/ tests/

# Sort imports
isort src/ tests/

# Type checking
mypy src/

# Linting
flake8 src/ tests/
```

### Building Documentation

```bash
# Generate documentation with pdoc
pdoc pdfparse --output-dir docs/

# Or with Sphinx (if configured)
cd docs/
make html
```

### Releasing

```bash
# Bump version (patch/minor/major)
bumpver update --patch

# Build package
python -m build

# Upload to PyPI (after configuring credentials)
twine upload dist/*
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and ensure code quality checks pass
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## Author

**James G Willmore**
- Email: willmorejg@gmail.com
- GitHub: [@willmorejg](https://github.com/willmorejg)

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a list of changes and version history.

## Support

If you encounter any issues or have questions:

1. Check the [documentation](https://pdfparse.readthedocs.io/)
2. Search existing [issues](https://github.com/willmorejg/pdfparse/issues)
3. Create a new issue if needed

## Acknowledgments

- Thanks to the Python packaging community for excellent tools and documentation
- Inspired by various PDF parsing libraries in the Python ecosystem
