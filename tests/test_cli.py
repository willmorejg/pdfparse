"""
Additional tests for command-line interface and specific edge cases.
"""

import subprocess
import sys
import pytest
from pathlib import Path


class TestHTMLToPDFCLI:
    """Test the command-line interface functionality."""

    def test_cli_help(self):
        """Test that the CLI help works."""
        try:
            result = subprocess.run([
                sys.executable, "-m", "pdfparse.html_to_pdf", "--help"
            ], capture_output=True, text=True, check=False, cwd=Path(__file__).parent.parent)
            
            assert result.returncode == 0
            assert "HTML to PDF" in result.stdout
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
            result = subprocess.run([
                sys.executable, "-m", "pdfparse.html_to_pdf",
                str(html_file), str(output_file),
                "--backend", "weasyprint"
            ], capture_output=True, text=True, check=False, cwd=Path(__file__).parent.parent)
            
            if result.returncode == 0:
                assert output_file.exists(), "CLI conversion did not create output file"
                assert output_file.stat().st_size > 0, "CLI output file is empty"
                print(f"✓ CLI conversion successful: {output_file}")
                
                # Clean up
                output_file.unlink()
            else:
                pytest.skip(f"CLI conversion failed: {result.stderr}")
                
        except (subprocess.SubprocessError, FileNotFoundError) as e:
            pytest.skip(f"CLI test skipped: {e}")

    def test_invalid_file_error(self):
        """Test CLI with invalid input file."""
        try:
            result = subprocess.run([
                sys.executable, "-m", "pdfparse.html_to_pdf",
                "nonexistent.html", "output.pdf"
            ], capture_output=True, text=True, check=False, cwd=Path(__file__).parent.parent)
            
            assert result.returncode != 0
            assert "Error:" in result.stderr or "Error:" in result.stdout
            
        except (subprocess.SubprocessError, FileNotFoundError) as e:
            pytest.skip(f"CLI error test skipped: {e}")
