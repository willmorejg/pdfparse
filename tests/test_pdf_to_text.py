# Copyright 2025 James G Willmore
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Tests for PDF to Text Parser

Comprehensive test suite for the PDFToTextParser class, covering all backends
and extraction functionality.
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from pdfparse.pdf_to_text import PDFToTextParser


class TestPDFToTextParser:
    """Test suite for PDFToTextParser class."""

    @pytest.fixture
    def sample_pdf_path(self):
        """Fixture providing path to sample PDF file."""
        test_data_dir = Path(__file__).parent / "test_data"
        pdf_path = test_data_dir / "sample_document.pdf"

        # Ensure the test PDF exists
        if not pdf_path.exists():
            pytest.skip(f"Test PDF not found: {pdf_path}")

        return str(pdf_path)

    @pytest.fixture
    def temp_pdf_path(self):
        """Fixture providing temporary PDF file path."""
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            temp_path = tmp.name
        yield temp_path
        # Cleanup
        try:
            os.unlink(temp_path)
        except OSError:
            pass

    @pytest.fixture
    def parser_pypdf(self):
        """Fixture providing PDFToTextParser with PyPDF backend."""
        return PDFToTextParser(backend="pypdf")

    @pytest.fixture
    def parser_pdfplumber(self):
        """Fixture providing PDFToTextParser with pdfplumber backend."""
        return PDFToTextParser(backend="pdfplumber")

    @pytest.fixture
    def parser_pymupdf(self):
        """Fixture providing PDFToTextParser with PyMuPDF backend."""
        return PDFToTextParser(backend="pymupdf")

    def test_parser_initialization_default_backend(self):
        """Test parser initialization with default backend."""
        parser = PDFToTextParser()
        assert parser.backend == "pypdf"

    def test_parser_initialization_custom_backend(self):
        """Test parser initialization with custom backend."""
        parser = PDFToTextParser(backend="pdfplumber")
        assert parser.backend == "pdfplumber"

    def test_parser_initialization_case_insensitive(self):
        """Test parser initialization is case insensitive."""
        parser = PDFToTextParser(backend="PyPDF")
        assert parser.backend == "pypdf"

    def test_invalid_backend_raises_error(self):
        """Test that invalid backend raises ValueError."""
        with pytest.raises(ValueError, match="Backend 'invalid' not supported"):
            PDFToTextParser(backend="invalid")

    def test_nonexistent_file_raises_error(self, parser_pypdf):
        """Test that nonexistent file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError, match="PDF file not found"):
            parser_pypdf.extract_text_from_file("nonexistent.pdf")

    def test_non_pdf_file_raises_error(self, parser_pypdf, temp_pdf_path):
        """Test that non-PDF file raises ValueError."""
        # Create a non-PDF file
        txt_path = temp_pdf_path.replace(".pdf", ".txt")
        with open(txt_path, "w") as f:
            f.write("This is not a PDF")

        try:
            with pytest.raises(ValueError, match="File must be a PDF"):
                parser_pypdf.extract_text_from_file(txt_path)
        finally:
            try:
                os.unlink(txt_path)
            except OSError:
                pass

    @pytest.mark.parametrize("backend", ["pypdf", "pdfplumber", "pymupdf"])
    def test_extract_text_from_file_all_backends(self, backend, sample_pdf_path):
        """Test text extraction from file works with all backends."""
        parser = PDFToTextParser(backend=backend)
        text = parser.extract_text_from_file(sample_pdf_path)

        assert isinstance(text, str)
        assert len(text) > 0
        # Check for expected content
        assert "PDF Parser Test Document" in text
        assert "Introduction" in text
        assert "searchable" in text

    def test_extract_text_with_specific_pages(self, parser_pypdf, sample_pdf_path):
        """Test text extraction from specific pages."""
        # Extract only first page (0-indexed)
        text = parser_pypdf.extract_text_from_file(sample_pdf_path, pages=[0])

        assert isinstance(text, str)
        assert len(text) > 0
        assert "Page 1" in text

    def test_extract_text_by_page(self, parser_pypdf, sample_pdf_path):
        """Test text extraction by page."""
        page_texts = parser_pypdf.extract_text_by_page(sample_pdf_path)

        assert isinstance(page_texts, dict)
        assert len(page_texts) >= 1
        # Check that page 0 exists and has content
        assert 0 in page_texts
        assert isinstance(page_texts[0], str)
        assert len(page_texts[0]) > 0

    def test_extract_text_with_clean_text_option(self, parser_pypdf, sample_pdf_path):
        """Test text extraction with clean_text option."""
        # Test with cleaning enabled (default)
        text_clean = parser_pypdf.extract_text_from_file(
            sample_pdf_path, clean_text=True
        )

        # Test with cleaning disabled
        text_raw = parser_pypdf.extract_text_from_file(
            sample_pdf_path, clean_text=False
        )

        assert isinstance(text_clean, str)
        assert isinstance(text_raw, str)
        # Both should have content
        assert len(text_clean) > 0
        assert len(text_raw) > 0

    def test_get_pdf_metadata(self, parser_pypdf, sample_pdf_path):
        """Test PDF metadata extraction."""
        metadata = parser_pypdf.get_pdf_metadata(sample_pdf_path)

        assert isinstance(metadata, dict)
        # Should at least have page count
        assert "pages" in metadata
        assert int(metadata["pages"]) >= 1

    def test_search_text_case_sensitive(self, parser_pypdf, sample_pdf_path):
        """Test text search with case sensitivity."""
        matches = parser_pypdf.search_text(
            sample_pdf_path, "searchable", case_sensitive=True
        )

        assert isinstance(matches, list)
        assert len(matches) > 0

        # Check structure of matches
        for match in matches:
            assert "page" in match
            assert "position" in match
            assert "context" in match
            assert "match" in match
            assert match["match"] == "searchable"

    def test_search_text_case_insensitive(self, parser_pypdf, sample_pdf_path):
        """Test text search with case insensitivity."""
        matches = parser_pypdf.search_text(
            sample_pdf_path, "SEARCHABLE", case_sensitive=False
        )

        assert isinstance(matches, list)
        assert len(matches) > 0

    def test_search_text_no_matches(self, parser_pypdf, sample_pdf_path):
        """Test text search with no matches."""
        matches = parser_pypdf.search_text(sample_pdf_path, "nonexistentword")

        assert isinstance(matches, list)
        assert len(matches) == 0

    def test_clean_text_function(self, parser_pypdf):
        """Test the _clean_text function."""
        # Test with various text issues
        dirty_text = "This  is   a    test\nwith\textra\r\nwhitespace"
        clean_text = parser_pypdf._clean_text(dirty_text)

        assert "This is a test with extra whitespace" in clean_text

    def test_clean_text_empty_string(self, parser_pypdf):
        """Test _clean_text with empty string."""
        result = parser_pypdf._clean_text("")
        assert result == ""

    def test_clean_text_none_input(self, parser_pypdf):
        """Test _clean_text with None input."""
        result = parser_pypdf._clean_text(None)
        assert result == ""

    def test_extract_text_with_path_object(self, parser_pypdf, sample_pdf_path):
        """Test text extraction with Path object instead of string."""
        path_obj = Path(sample_pdf_path)
        text = parser_pypdf.extract_text_from_file(path_obj)

        assert isinstance(text, str)
        assert len(text) > 0

    def test_extract_text_by_page_with_path_object(self, parser_pypdf, sample_pdf_path):
        """Test page-by-page extraction with Path object."""
        path_obj = Path(sample_pdf_path)
        page_texts = parser_pypdf.extract_text_by_page(path_obj)

        assert isinstance(page_texts, dict)
        assert len(page_texts) >= 1

    def test_get_metadata_with_path_object(self, parser_pypdf, sample_pdf_path):
        """Test metadata extraction with Path object."""
        path_obj = Path(sample_pdf_path)
        metadata = parser_pypdf.get_pdf_metadata(path_obj)

        assert isinstance(metadata, dict)
        assert "pages" in metadata

    def test_search_text_with_path_object(self, parser_pypdf, sample_pdf_path):
        """Test text search with Path object."""
        path_obj = Path(sample_pdf_path)
        matches = parser_pypdf.search_text(path_obj, "test")

        assert isinstance(matches, list)

    @patch("pdfparse.pdf_to_text.logger")
    def test_extraction_error_handling(self, mock_logger, parser_pypdf):
        """Test error handling during text extraction."""
        with pytest.raises(FileNotFoundError):
            parser_pypdf.extract_text_from_file("nonexistent.pdf")

    def test_backend_validation_basic(self):
        """Test basic backend validation functionality."""
        # Test that valid backends work
        parser = PDFToTextParser(backend="pypdf")
        assert parser.backend == "pypdf"

        # Verify validate_backend doesn't raise for valid backends
        parser.validate_backend()  # Should not raise

    def test_page_cache_usage(self, parser_pypdf, sample_pdf_path):
        """Test that page cache is used properly."""
        # The cache is internal, but we can test that repeated calls work
        text1 = parser_pypdf.extract_text_from_file(sample_pdf_path)
        text2 = parser_pypdf.extract_text_from_file(sample_pdf_path)

        assert text1 == text2

    def test_extract_with_invalid_pages(self, parser_pypdf, sample_pdf_path):
        """Test extraction with invalid page numbers."""
        # Request page that doesn't exist
        text = parser_pypdf.extract_text_from_file(sample_pdf_path, pages=[999])

        # Should return empty or minimal content
        assert isinstance(text, str)

    def test_extract_with_empty_pages_list(self, parser_pypdf, sample_pdf_path):
        """Test extraction with empty pages list."""
        text = parser_pypdf.extract_text_from_file(sample_pdf_path, pages=[])

        # Should return empty content
        assert isinstance(text, str)

    def test_multiple_backend_consistency(self, sample_pdf_path):
        """Test that different backends produce similar results."""
        backends = ["pypdf", "pdfplumber", "pymupdf"]
        results = {}

        for backend in backends:
            try:
                parser = PDFToTextParser(backend=backend)
                text = parser.extract_text_from_file(sample_pdf_path)
                results[backend] = text
            except ImportError:
                # Skip if backend not available
                pytest.skip(f"Backend {backend} not available")

        # Check that all backends extracted some text
        for backend, text in results.items():
            assert len(text) > 0, f"Backend {backend} produced no text"

        # Check that they all contain key terms
        for backend, text in results.items():
            assert (
                "PDF Parser Test Document" in text or "PDF" in text
            ), f"Backend {backend} missing key content"


class TestPDFToTextParserIntegration:
    """Integration tests for PDFToTextParser."""

    @pytest.fixture
    def sample_pdf_path(self):
        """Fixture providing path to sample PDF file."""
        test_data_dir = Path(__file__).parent / "test_data"
        pdf_path = test_data_dir / "sample_document.pdf"

        # Ensure the test PDF exists
        if not pdf_path.exists():
            pytest.skip(f"Test PDF not found: {pdf_path}")

        return str(pdf_path)

    @pytest.fixture
    def parser_pypdf(self):
        """Fixture providing PDFToTextParser with PyPDF backend."""
        return PDFToTextParser(backend="pypdf")

    def test_full_workflow_pypdf(self, sample_pdf_path):
        """Test complete workflow with PyPDF backend."""
        parser = PDFToTextParser(backend="pypdf")

        # Extract all text
        full_text = parser.extract_text_from_file(sample_pdf_path)
        assert len(full_text) > 0

        # Extract by page
        page_texts = parser.extract_text_by_page(sample_pdf_path)
        assert len(page_texts) >= 1

        # Get metadata
        metadata = parser.get_pdf_metadata(sample_pdf_path)
        assert "pages" in metadata

        # Search text
        matches = parser.search_text(sample_pdf_path, "test")
        assert isinstance(matches, list)

    def test_error_recovery(self, parser_pypdf):
        """Test that parser recovers from errors gracefully."""
        # Test with non-existent file
        with pytest.raises(FileNotFoundError):
            parser_pypdf.extract_text_from_file("does_not_exist.pdf")

        # Parser should still work after error
        assert parser_pypdf.backend == "pypdf"
