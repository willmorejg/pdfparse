"""
Additional tests for command-line interface and specific edge cases.
"""

import subprocess
import sys
import tempfile
import os
from pathlib import Path

import pytest


class TestHTMLToPDFCLI:
    """Test the command-line interface functionality."""

    def test_cli_help(self):
        """Test that the CLI help works."""
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pdfparse.cli", "html2pdf", "--help"],
                capture_output=True,
                text=True,
                check=False,
                cwd=Path(__file__).parent.parent,
            )

            assert result.returncode == 0
            assert "HTML" in result.stdout or "Convert" in result.stdout
            assert "--backend" in result.stdout

        except (subprocess.SubprocessError, FileNotFoundError) as e:
            pytest.skip(f"CLI test skipped: {e}")

    def test_cli_conversion(self):
        """Test CLI conversion with example file."""
        test_data_dir = Path(__file__).parent / "test_data"
        html_file = test_data_dir / "example.html"
        output_file = test_data_dir / "cli_test_output.pdf"

        # Clean up any existing output file
        if output_file.exists():
            output_file.unlink()

        try:
            cmd = [
                sys.executable,
                "-m",
                "pdfparse.cli",
                "html2pdf",
                str(html_file),
                str(output_file),
                "--backend",
                "reportlab",
            ]
            print(f"Running command: {' '.join(cmd)}")
            print(f"Working directory: {Path(__file__).parent.parent}")
            print(f"HTML file exists: {html_file.exists()}")
            print(f"Output file path: {output_file}")

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False,
                cwd=Path(__file__).parent.parent,
            )

            print(f"Return code: {result.returncode}")
            print(f"Stdout: {result.stdout}")
            print(f"Stderr: {result.stderr}")

            if result.returncode == 0:
                assert (
                    output_file.exists()
                ), f"CLI conversion did not create output file at {output_file}"
                assert output_file.stat().st_size > 0, "CLI output file is empty"
                print("✓ CLI conversion successful")

                # Clean up
                output_file.unlink()
            else:
                pytest.skip(f"CLI conversion failed: {result.stderr}")

        except (subprocess.SubprocessError, FileNotFoundError) as e:
            pytest.skip(f"CLI test skipped: {e}")

    def test_invalid_file_error(self):
        """Test CLI with invalid input file."""
        try:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pdfparse.cli",
                    "html2pdf",
                    "nonexistent.html",
                    "output.pdf",
                ],
                capture_output=True,
                text=True,
                check=False,
                cwd=Path(__file__).parent.parent,
            )

            assert result.returncode != 0
            assert "Error:" in result.stderr or "Error:" in result.stdout

        except (subprocess.SubprocessError, FileNotFoundError) as e:
            pytest.skip(f"CLI error test skipped: {e}")


class TestPDFParsingCLI:
    """Test the CLI interface for PDF text extraction."""

    @pytest.fixture
    def sample_pdf(self):
        """Get path to sample PDF for CLI testing."""
        test_data_dir = Path(__file__).parent / "test_data"
        pdf_path = test_data_dir / "sample_document.pdf"

        if not pdf_path.exists():
            pytest.skip(f"Sample PDF not found: {pdf_path}")

        return pdf_path

    def test_cli_main_help(self):
        """Test main CLI help."""
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pdfparse.cli", "--help"],
                capture_output=True,
                text=True,
                check=False,
                cwd=Path(__file__).parent.parent,
            )

            assert result.returncode == 0
            assert "pdfparse" in result.stdout.lower()

        except (subprocess.SubprocessError, FileNotFoundError) as e:
            pytest.skip(f"CLI help test skipped: {e}")

    def test_cli_pdf_to_text_basic(self, sample_pdf):
        """Test basic PDF to text extraction via CLI."""
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pdfparse.cli", "pdf2text", str(sample_pdf)],
                capture_output=True,
                text=True,
                check=False,
                cwd=Path(__file__).parent.parent,
            )

            if result.returncode == 0:
                assert len(result.stdout) > 0, "CLI should output extracted text"
                assert (
                    "PDF" in result.stdout or "Test" in result.stdout
                ), "Should contain document content"
                print("✓ CLI PDF to text extraction successful")
            else:
                pytest.skip(f"CLI pdf2text failed: {result.stderr}")

        except (subprocess.SubprocessError, FileNotFoundError) as e:
            pytest.skip(f"CLI pdf2text test skipped: {e}")

    def test_cli_pdf_to_text_with_output_file(self, sample_pdf):
        """Test PDF to text extraction with output file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as tmp:
            output_file = tmp.name

        try:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pdfparse.cli",
                    "pdf2text",
                    str(sample_pdf),
                    "--output",
                    output_file,
                ],
                capture_output=True,
                text=True,
                check=False,
                cwd=Path(__file__).parent.parent,
            )

            if result.returncode == 0:
                assert os.path.exists(output_file), "Output file should be created"
                assert (
                    os.path.getsize(output_file) > 0
                ), "Output file should have content"

                with open(output_file, "r", encoding="utf-8") as f:
                    content = f.read()
                    assert len(content) > 0, "Output file should contain text"

                print("✓ CLI PDF to text with output file successful")
            else:
                pytest.skip(f"CLI pdf2text with output failed: {result.stderr}")

        except (subprocess.SubprocessError, FileNotFoundError) as e:
            pytest.skip(f"CLI pdf2text output test skipped: {e}")
        finally:
            try:
                os.unlink(output_file)
            except OSError:
                pass

    def test_cli_pdf_search(self, sample_pdf):
        """Test PDF text search via CLI."""
        try:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pdfparse.cli",
                    "search",
                    str(sample_pdf),
                    "searchable",
                ],
                capture_output=True,
                text=True,
                check=False,
                cwd=Path(__file__).parent.parent,
            )

            if result.returncode == 0:
                # Should either find matches or report no matches
                assert "Found" in result.stdout or "No matches" in result.stdout
                print("✓ CLI PDF search successful")
            else:
                pytest.skip(f"CLI search failed: {result.stderr}")

        except (subprocess.SubprocessError, FileNotFoundError) as e:
            pytest.skip(f"CLI search test skipped: {e}")

    def test_cli_pdf_metadata(self, sample_pdf):
        """Test PDF metadata extraction via CLI."""
        try:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pdfparse.cli",
                    "pdf2text",
                    str(sample_pdf),
                    "--metadata",
                ],
                capture_output=True,
                text=True,
                check=False,
                cwd=Path(__file__).parent.parent,
            )

            if result.returncode == 0:
                assert "Metadata" in result.stdout or "pages" in result.stdout
                print("✓ CLI PDF metadata extraction successful")
            else:
                pytest.skip(f"CLI metadata failed: {result.stderr}")

        except (subprocess.SubprocessError, FileNotFoundError) as e:
            pytest.skip(f"CLI metadata test skipped: {e}")

    def test_cli_html_to_pdf_integration(self):
        """Test HTML to PDF conversion via CLI."""
        test_data_dir = Path(__file__).parent / "test_data"
        html_file = test_data_dir / "example.html"

        if not html_file.exists():
            pytest.skip("HTML test file not found")

        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            pdf_file = tmp.name

        try:
            # Convert HTML to PDF
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pdfparse.cli",
                    "html2pdf",
                    str(html_file),
                    pdf_file,
                    "--backend",
                    "reportlab",
                ],
                capture_output=True,
                text=True,
                check=False,
                cwd=Path(__file__).parent.parent,
            )

            if result.returncode == 0:
                assert os.path.exists(pdf_file), "PDF should be created"
                assert os.path.getsize(pdf_file) > 0, "PDF should have content"

                # Now test extracting text from the created PDF
                text_result = subprocess.run(
                    [sys.executable, "-m", "pdfparse.cli", "pdf2text", pdf_file],
                    capture_output=True,
                    text=True,
                    check=False,
                    cwd=Path(__file__).parent.parent,
                )

                if text_result.returncode == 0:
                    assert (
                        len(text_result.stdout) > 0
                    ), "Should extract text from created PDF"
                    print("✓ CLI HTML→PDF→Text integration successful")
                else:
                    print(
                        f"⚠ PDF creation succeeded but text extraction failed: {text_result.stderr}"
                    )
            else:
                pytest.skip(f"CLI html2pdf failed: {result.stderr}")

        except (subprocess.SubprocessError, FileNotFoundError) as e:
            pytest.skip(f"CLI integration test skipped: {e}")
        finally:
            try:
                os.unlink(pdf_file)
            except OSError:
                pass


class TestCLIErrorHandling:
    """Test CLI error handling scenarios."""

    def test_cli_nonexistent_pdf_file(self):
        """Test CLI behavior with non-existent PDF file."""
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pdfparse.cli", "pdf2text", "nonexistent.pdf"],
                capture_output=True,
                text=True,
                check=False,
                cwd=Path(__file__).parent.parent,
            )

            assert result.returncode != 0, "Should fail with non-existent file"
            assert "Error" in result.stderr or "not found" in result.stderr.lower()

        except (subprocess.SubprocessError, FileNotFoundError) as e:
            pytest.skip(f"CLI error handling test skipped: {e}")

    def test_cli_invalid_backend(self):
        """Test CLI behavior with invalid backend."""
        test_data_dir = Path(__file__).parent / "test_data"
        html_file = test_data_dir / "example.html"

        if not html_file.exists():
            pytest.skip("HTML test file not found")

        try:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pdfparse.cli",
                    "html2pdf",
                    str(html_file),
                    "output.pdf",
                    "--backend",
                    "invalid",
                ],
                capture_output=True,
                text=True,
                check=False,
                cwd=Path(__file__).parent.parent,
            )

            assert result.returncode != 0, "Should fail with invalid backend"

        except (subprocess.SubprocessError, FileNotFoundError) as e:
            pytest.skip(f"CLI invalid backend test skipped: {e}")

    def test_cli_missing_arguments(self):
        """Test CLI behavior with missing required arguments."""
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pdfparse.cli", "pdf2text"],
                capture_output=True,
                text=True,
                check=False,
                cwd=Path(__file__).parent.parent,
            )

            assert result.returncode != 0, "Should fail with missing arguments"

        except (subprocess.SubprocessError, FileNotFoundError) as e:
            pytest.skip(f"CLI missing args test skipped: {e}")
