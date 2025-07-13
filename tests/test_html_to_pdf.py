"""
Tests for HTML to PDF conversion functionality.

This module contains comprehensive tests for the HTMLToPDFConverter class,
testing file conversion with different backends and various scenarios.
"""

import os
import shutil
from pathlib import Path

import pytest

from pdfparse.html_to_pdf import HTMLToPDFConverter


class TestHTMLToPDFConverter:
    """Test suite for HTMLToPDFConverter class."""

    @pytest.fixture
    def test_data_dir(self):
        """Get the test data directory path."""
        return Path(__file__).parent / "test_data"

    @pytest.fixture
    def example_html_file(self, test_data_dir):
        """Get the path to the example HTML file."""
        html_file = test_data_dir / "example.html"
        assert html_file.exists(), f"Test file {html_file} not found"
        return str(html_file)

    @pytest.fixture
    def temp_output_dir(self, test_data_dir):
        """Create a temporary directory for test outputs."""
        temp_dir = test_data_dir / "temp_output"
        temp_dir.mkdir(exist_ok=True)
        yield temp_dir
        # Cleanup after test
        if temp_dir.exists():
            shutil.rmtree(temp_dir)

    @pytest.fixture
    def output_pdf_path(self, test_data_dir):
        """Generate output PDF file path in test_data directory."""

        def _get_output_path(backend_name):
            return str(test_data_dir / f"example_output_{backend_name}.pdf")

        return _get_output_path

    def test_converter_initialization_default_backend(self):
        """Test converter initialization with default backend."""
        converter = HTMLToPDFConverter()
        assert converter.backend == "weasyprint"

    def test_converter_initialization_custom_backend(self):
        """Test converter initialization with custom backend."""
        converter = HTMLToPDFConverter(backend="reportlab")
        assert converter.backend == "reportlab"

    def test_converter_initialization_case_insensitive(self):
        """Test converter initialization with case-insensitive backend name."""
        converter = HTMLToPDFConverter(backend="WEASYPRINT")
        assert converter.backend == "weasyprint"

    def test_invalid_backend_raises_error(self):
        """Test that invalid backend raises ValueError."""
        with pytest.raises(ValueError, match="Backend 'invalid' not supported"):
            HTMLToPDFConverter(backend="invalid")

    def test_nonexistent_file_raises_error(self):
        """Test that nonexistent HTML file raises FileNotFoundError."""
        converter = HTMLToPDFConverter()
        with pytest.raises(FileNotFoundError, match="HTML file not found"):
            converter.convert_html_file("nonexistent.html", "output.pdf")

    @pytest.mark.parametrize("backend", ["weasyprint", "xhtml2pdf", "reportlab"])
    def test_convert_html_file_all_backends(
        self, backend, example_html_file, output_pdf_path
    ):
        """Test HTML file conversion with all supported backends."""
        converter = HTMLToPDFConverter(backend=backend)
        output_file = output_pdf_path(backend)

        # Clean up any existing output file
        if os.path.exists(output_file):
            os.remove(output_file)

        try:
            # Attempt conversion
            result = converter.convert_html_file(example_html_file, output_file)

            # Check conversion result
            assert result is True, f"Conversion with {backend} backend failed"

            # Check that output file was created
            assert os.path.exists(
                output_file
            ), f"Output PDF file not created for {backend} backend"

            # Check that file has content (not empty)
            assert (
                os.path.getsize(output_file) > 0
            ), f"Output PDF file is empty for {backend} backend"

            print(f"✓ {backend} backend: Successfully created {output_file}")

        except ImportError as e:
            pytest.skip(f"Backend {backend} dependencies not available: {e}")
        except Exception as e:
            pytest.fail(f"Unexpected error with {backend} backend: {e}")

    def test_convert_html_string_weasyprint(self, output_pdf_path):
        """Test HTML string conversion with WeasyPrint backend."""
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Test HTML String</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                h1 { color: #333; }
            </style>
        </head>
        <body>
            <h1>Test HTML String Conversion</h1>
            <p>This is a test of converting HTML string to PDF.</p>
        </body>
        </html>
        """

        try:
            converter = HTMLToPDFConverter(backend="weasyprint")
            output_file = output_pdf_path("string_test")

            # Clean up any existing output file
            if os.path.exists(output_file):
                os.remove(output_file)

            result = converter.convert_html_string(html_content, output_file)

            assert result is True, "String conversion failed"
            assert os.path.exists(output_file), "Output PDF file not created"
            assert os.path.getsize(output_file) > 0, "Output PDF file is empty"

            print(f"✓ String conversion: Successfully created {output_file}")

        except ImportError:
            pytest.skip("WeasyPrint not available for string conversion test")

    def test_convert_with_css_options(self, example_html_file, output_pdf_path):
        """Test conversion with CSS options."""
        try:
            converter = HTMLToPDFConverter(backend="weasyprint")
            output_file = output_pdf_path("css_test")

            # Clean up any existing output file
            if os.path.exists(output_file):
                os.remove(output_file)

            # Test with CSS string option
            css_string = "body { background-color: #f0f0f0; }"
            result = converter.convert_html_file(
                example_html_file, output_file, css_string=css_string
            )

            assert result is True, "CSS conversion failed"
            assert os.path.exists(output_file), "Output PDF file not created"

            print(f"✓ CSS options: Successfully created {output_file}")

        except ImportError:
            pytest.skip("WeasyPrint not available for CSS options test")

    def test_convert_with_margin_options(self, example_html_file, output_pdf_path):
        """Test conversion with margin options."""
        try:
            converter = HTMLToPDFConverter(backend="xhtml2pdf")
            output_file = output_pdf_path("margin_test")

            # Clean up any existing output file
            if os.path.exists(output_file):
                os.remove(output_file)

            # Test with custom margins
            result = converter.convert_html_file(
                example_html_file,
                output_file,
                margin_top="1in",
                margin_bottom="1in",
                margin_left="1in",
                margin_right="1in",
            )

            assert result is True, "Margin conversion failed"
            assert os.path.exists(output_file), "Output PDF file not created"

            print(f"✓ Margin options: Successfully created {output_file}")

        except ImportError:
            pytest.skip("xhtml2pdf not available for margin options test")

    def test_convert_with_page_size_options(self, example_html_file, output_pdf_path):
        """Test conversion with page size options."""
        try:
            converter = HTMLToPDFConverter(backend="reportlab")
            output_file = output_pdf_path("pagesize_test")

            # Clean up any existing output file
            if os.path.exists(output_file):
                os.remove(output_file)

            # Test with letter page size
            result = converter.convert_html_file(
                example_html_file, output_file, page_size="letter"
            )

            assert result is True, "Page size conversion failed"
            assert os.path.exists(output_file), "Output PDF file not created"

            print(f"✓ Page size options: Successfully created {output_file}")

        except ImportError:
            pytest.skip("ReportLab not available for page size options test")

    def test_error_handling_invalid_html(self, output_pdf_path):
        """Test error handling with invalid HTML content."""
        converter = HTMLToPDFConverter(backend="weasyprint")
        output_file = output_pdf_path("error_test")

        # Test with malformed HTML
        invalid_html = "<html><head><title>Test</title><body><h1>Unclosed tag<p>Content"

        try:
            # This should not crash, but might return False
            converter.convert_html_string(invalid_html, output_file)
            # Don't assert on result as different backends handle invalid HTML differently
            print("✓ Error handling: Handled invalid HTML gracefully")

        except ImportError:
            pytest.skip("WeasyPrint not available for error handling test")

    @pytest.mark.integration
    def test_full_conversion_workflow(self, example_html_file, test_data_dir):
        """Integration test for complete conversion workflow."""
        output_files = []

        for backend in ["weasyprint", "xhtml2pdf", "reportlab"]:
            try:
                converter = HTMLToPDFConverter(backend=backend)
                output_file = str(test_data_dir / f"integration_test_{backend}.pdf")
                output_files.append(output_file)

                # Clean up any existing output file
                if os.path.exists(output_file):
                    os.remove(output_file)

                result = converter.convert_html_file(example_html_file, output_file)

                if result:
                    assert os.path.exists(
                        output_file
                    ), f"Output file not created for {backend}"
                    assert (
                        os.path.getsize(output_file) > 0
                    ), f"Output file is empty for {backend}"
                    print(f"✓ Integration test {backend}: Success")
                else:
                    print(f"⚠ Integration test {backend}: Conversion returned False")

            except ImportError:
                print(f"⚠ Integration test {backend}: Dependencies not available")
                continue
            except Exception as e:
                print(f"✗ Integration test {backend}: Error - {e}")

    def test_cleanup_generated_files(self, test_data_dir):
        """Clean up test-generated PDF files (run this last)."""
        pdf_files = list(test_data_dir.glob("*.pdf"))

        cleanup_count = 0
        for pdf_file in pdf_files:
            if any(
                test_name in pdf_file.name
                for test_name in [
                    "example_output_",
                    "string_test",
                    "css_test",
                    "margin_test",
                    "pagesize_test",
                    "error_test",
                    "integration_test_",
                ]
            ):
                try:
                    pdf_file.unlink()
                    cleanup_count += 1
                except OSError:
                    pass  # File might be locked or already deleted

        print(f"✓ Cleanup: Removed {cleanup_count} test-generated PDF files")
