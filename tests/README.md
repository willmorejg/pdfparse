# PDFParse Tests

This directory contains comprehensive tests for the PDFParse HTML to PDF conversion functionality.

## Test Structure

```
tests/
├── __init__.py              # Test package initialization
├── conftest.py              # Pytest configuration and shared fixtures
├── test_html_to_pdf.py      # Main HTML to PDF conversion tests
├── test_cli.py              # Command-line interface tests
└── test_data/
    └── example.html         # Sample HTML file for testing
```

## Test Files

### `test_html_to_pdf.py`
Main test suite covering:
- **Backend Testing**: Tests all three PDF backends (WeasyPrint, xhtml2pdf, ReportLab)
- **File Conversion**: Tests converting HTML files to PDF
- **String Conversion**: Tests converting HTML strings to PDF
- **Options Testing**: Tests various conversion options (CSS, margins, page size)
- **Error Handling**: Tests error scenarios and edge cases
- **Integration Testing**: Full workflow testing

### `test_cli.py`  
Command-line interface tests covering:
- **Help Command**: Tests `--help` functionality
- **File Conversion**: Tests CLI file conversion
- **Error Handling**: Tests CLI error scenarios

### `test_data/example.html`
Sample HTML file containing:
- Various HTML elements (headings, paragraphs, lists, tables)
- CSS styling (fonts, colors, layouts)
- Complex content for comprehensive testing

## Running Tests

### Run All Tests
```bash
python -m pytest tests/ -v
```

### Run Specific Test File
```bash
python -m pytest tests/test_html_to_pdf.py -v
```

### Run with Coverage
```bash
python -m pytest tests/ --cov=src/pdfparse --cov-report=term-missing
```

### Run Integration Tests Only
```bash
python -m pytest tests/ -m integration -v
```

### Run Test Suite with Custom Runner
```bash
python run_tests.py
```

## Test Features

### Parametrized Tests
Tests are parametrized to run with all supported backends:
- WeasyPrint (recommended)
- xhtml2pdf  
- ReportLab

### Fixtures
- `test_data_dir`: Path to test data directory
- `example_html_file`: Path to example HTML file
- `output_pdf_path`: Generator for output PDF file paths

### Markers
- `@pytest.mark.integration`: Marks integration tests

### Automatic Cleanup
Tests automatically clean up generated PDF files after completion.

## Output Files

During testing, PDF files are generated in `tests/test_data/`:
- `example_output_weasyprint.pdf`
- `example_output_xhtml2pdf.pdf`
- `example_output_reportlab.pdf`
- Additional test-specific output files

These files are automatically cleaned up by the test suite.

## Test Coverage

Current test coverage:
- **HTML to PDF Module**: ~83% coverage
- **Overall Package**: ~81% coverage

Missing coverage primarily in:
- Error handling edge cases
- Backend-specific error scenarios
- CLI module (separate from main conversion logic)

## Backend Dependencies

Tests will automatically skip if backend dependencies are not available:
- **WeasyPrint**: Requires `weasyprint` package
- **xhtml2pdf**: Requires `xhtml2pdf` package  
- **ReportLab**: Requires `reportlab` and `beautifulsoup4` packages

All dependencies are included in the `[dev]` extras install:
```bash
pip install -e ".[dev]"
```
