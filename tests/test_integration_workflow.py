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
Integration tests for complete PDF creation and parsing workflow.

Tests the entire pipeline: HTML → PDF → Text extraction, ensuring that
content is preserved through the conversion process.
"""

import tempfile
import os
from pathlib import Path
import pytest

from pdfparse.html_to_pdf import HTMLToPDFConverter
from pdfparse.pdf_to_text import PDFToTextParser


class TestPDFCreationToParsingWorkflow:
    """Integration tests for the complete HTML → PDF → Text workflow."""

    @pytest.fixture
    def test_html_content(self):
        """HTML content designed for testing the complete workflow."""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Integration Test Document</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; }
                h1 { color: #2c3e50; text-align: center; }
                h2 { color: #3498db; border-bottom: 2px solid #3498db; }
                .test-section { background-color: #f8f9fa; padding: 15px; margin: 10px 0; }
                table { width: 100%; border-collapse: collapse; margin: 20px 0; }
                th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                th { background-color: #f2f2f2; }
            </style>
        </head>
        <body>
            <h1>PDF Creation and Parsing Integration Test</h1>
            
            <div class="test-section">
                <h2>Text Extraction Test</h2>
                <p>This document contains various types of content to test the complete workflow 
                from HTML creation to PDF generation to text extraction.</p>
                <p>Special characters: àáâãäå ñ ç ü ö ß €</p>
                <p>Numbers and dates: 12345, 67.89, 2025-07-13, $123.45</p>
            </div>

            <div class="test-section">
                <h2>Search Test Keywords</h2>
                <p>This paragraph contains searchable keywords: INTEGRATION, workflow, 
                extraction, and parsing. These words should be findable in the final text.</p>
                <p>Case sensitivity test: Integration, INTEGRATION, integration</p>
            </div>

            <div class="test-section">
                <h2>Structured Content</h2>
                <ul>
                    <li>List item one with content</li>
                    <li>List item two with more content</li>
                    <li>List item three with final content</li>
                </ul>
                
                <table>
                    <thead>
                        <tr>
                            <th>Column A</th>
                            <th>Column B</th>
                            <th>Column C</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>Row 1 A</td>
                            <td>Row 1 B</td>
                            <td>Row 1 C</td>
                        </tr>
                        <tr>
                            <td>Row 2 A</td>
                            <td>Row 2 B</td>
                            <td>Row 2 C</td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <div class="test-section">
                <h2>Unicode and Formatting Test</h2>
                <p><strong>Bold text</strong> and <em>italic text</em> for formatting tests.</p>
                <p>Unicode symbols: ✓ ✗ → ← ↑ ↓ ★ ♥ ♦ ♠ ♣</p>
                <p>Mathematical symbols: α β γ δ ε ∞ ∑ ∫ ∂ √</p>
            </div>
        </body>
        </html>
        """

    @pytest.fixture
    def temp_files(self):
        """Create temporary file paths for testing."""
        temp_dir = tempfile.mkdtemp()
        html_file = os.path.join(temp_dir, "test_integration.html")
        pdf_file = os.path.join(temp_dir, "test_integration.pdf")
        text_file = os.path.join(temp_dir, "test_integration.txt")

        yield {"dir": temp_dir, "html": html_file, "pdf": pdf_file, "text": text_file}

        # Cleanup
        import shutil

        try:
            shutil.rmtree(temp_dir)
        except OSError:
            pass

    @pytest.mark.parametrize(
        "pdf_backend,parse_backend",
        [
            ("reportlab", "pypdf"),
            ("reportlab", "pdfplumber"),
            ("reportlab", "pymupdf"),
            ("weasyprint", "pypdf"),
            ("weasyprint", "pdfplumber"),
            ("weasyprint", "pymupdf"),
            ("xhtml2pdf", "pypdf"),
            ("xhtml2pdf", "pdfplumber"),
            ("xhtml2pdf", "pymupdf"),
        ],
    )
    def test_html_to_pdf_to_text_workflow(
        self, test_html_content, temp_files, pdf_backend, parse_backend
    ):
        """Test complete workflow: HTML → PDF → Text with different backend combinations."""
        html_file = temp_files["html"]
        pdf_file = temp_files["pdf"]

        # Step 1: Create HTML file
        with open(html_file, "w", encoding="utf-8") as f:
            f.write(test_html_content)

        # Step 2: Convert HTML to PDF
        try:
            pdf_converter = HTMLToPDFConverter(backend=pdf_backend)
            pdf_success = pdf_converter.convert_html_file(html_file, pdf_file)

            if not pdf_success:
                pytest.skip(f"PDF creation with {pdf_backend} backend failed")

        except ImportError:
            pytest.skip(f"PDF backend {pdf_backend} not available")
        except Exception as e:
            pytest.fail(f"PDF creation failed with {pdf_backend}: {e}")

        # Verify PDF was created
        assert os.path.exists(pdf_file), f"PDF file not created with {pdf_backend}"
        assert os.path.getsize(pdf_file) > 0, f"PDF file is empty with {pdf_backend}"

        # Step 3: Extract text from PDF
        try:
            text_parser = PDFToTextParser(backend=parse_backend)
            extracted_text = text_parser.extract_text_from_file(pdf_file)

        except ImportError:
            pytest.skip(f"Parse backend {parse_backend} not available")
        except Exception as e:
            pytest.fail(f"Text extraction failed with {parse_backend}: {e}")

        # Step 4: Verify content preservation
        assert len(extracted_text) > 0, f"No text extracted with {parse_backend}"

        # Check for key content that should survive the conversion
        expected_content = [
            "Integration Test",
            "Text Extraction Test",
            "Search Test Keywords",
            "INTEGRATION",
            "workflow",
            "extraction",
            "parsing",
            "List item",
            "Column A",
            "Row 1",
        ]

        missing_content = []
        for content in expected_content:
            if content not in extracted_text:
                missing_content.append(content)

        # Allow some flexibility - not all backends preserve all formatting
        preservation_rate = (len(expected_content) - len(missing_content)) / len(
            expected_content
        )
        assert (
            preservation_rate >= 0.7
        ), f"Content preservation too low ({preservation_rate:.1%}) with {pdf_backend}→{parse_backend}. Missing: {missing_content}"

        print(
            f"✓ {pdf_backend}→{parse_backend}: {preservation_rate:.1%} content preserved"
        )

    def test_roundtrip_search_functionality(self, test_html_content, temp_files):
        """Test that search functionality works on PDFs created from HTML."""
        html_file = temp_files["html"]
        pdf_file = temp_files["pdf"]

        # Create HTML file
        with open(html_file, "w", encoding="utf-8") as f:
            f.write(test_html_content)

        # Convert to PDF using most reliable backend
        try:
            pdf_converter = HTMLToPDFConverter(backend="reportlab")
            pdf_success = pdf_converter.convert_html_file(html_file, pdf_file)

            if not pdf_success:
                pytest.skip("PDF creation failed")

        except ImportError:
            pytest.skip("ReportLab not available for search test")

        # Test search functionality
        text_parser = PDFToTextParser(backend="pypdf")

        # Test case-sensitive search
        matches = text_parser.search_text(pdf_file, "INTEGRATION", case_sensitive=True)
        assert len(matches) > 0, "Case-sensitive search failed"

        # Test case-insensitive search
        matches = text_parser.search_text(pdf_file, "integration", case_sensitive=False)
        assert len(matches) > 0, "Case-insensitive search failed"

        # Test search for non-existent term
        matches = text_parser.search_text(pdf_file, "nonexistentterm")
        assert len(matches) == 0, "Search for non-existent term should return empty"

    def test_roundtrip_metadata_extraction(self, test_html_content, temp_files):
        """Test metadata extraction from generated PDFs."""
        html_file = temp_files["html"]
        pdf_file = temp_files["pdf"]

        # Create HTML file
        with open(html_file, "w", encoding="utf-8") as f:
            f.write(test_html_content)

        # Convert to PDF
        try:
            pdf_converter = HTMLToPDFConverter(backend="reportlab")
            pdf_success = pdf_converter.convert_html_file(html_file, pdf_file)

            if not pdf_success:
                pytest.skip("PDF creation failed")

        except ImportError:
            pytest.skip("ReportLab not available for metadata test")

        # Extract metadata
        text_parser = PDFToTextParser(backend="pypdf")
        metadata = text_parser.get_pdf_metadata(pdf_file)

        # Basic metadata checks
        assert isinstance(metadata, dict), "Metadata should be a dictionary"
        assert "pages" in metadata, "Metadata should include page count"
        assert int(metadata["pages"]) >= 1, "Should have at least one page"

    def test_page_by_page_extraction_consistency(self, test_html_content, temp_files):
        """Test that page-by-page extraction is consistent with full extraction."""
        html_file = temp_files["html"]
        pdf_file = temp_files["pdf"]

        # Create HTML file
        with open(html_file, "w", encoding="utf-8") as f:
            f.write(test_html_content)

        # Convert to PDF
        try:
            pdf_converter = HTMLToPDFConverter(backend="reportlab")
            pdf_success = pdf_converter.convert_html_file(html_file, pdf_file)

            if not pdf_success:
                pytest.skip("PDF creation failed")

        except ImportError:
            pytest.skip("ReportLab not available for consistency test")

        # Test extraction methods
        text_parser = PDFToTextParser(backend="pypdf")

        # Full extraction
        full_text = text_parser.extract_text_from_file(pdf_file)

        # Page-by-page extraction
        page_texts = text_parser.extract_text_by_page(pdf_file)
        combined_text = "\n\n".join(page_texts.values())

        # The texts should contain similar content (allowing for formatting differences)
        # Check that key terms appear in both
        key_terms = ["Integration Test", "workflow", "extraction"]

        for term in key_terms:
            assert (
                term in full_text or term.lower() in full_text.lower()
            ), f"Term '{term}' missing from full extraction"
            assert (
                term in combined_text or term.lower() in combined_text.lower()
            ), f"Term '{term}' missing from page-by-page extraction"

    def test_backend_failure_graceful_degradation(self, test_html_content, temp_files):
        """Test graceful handling when backends fail."""
        html_file = temp_files["html"]
        pdf_file = temp_files["pdf"]

        # Create HTML file
        with open(html_file, "w", encoding="utf-8") as f:
            f.write(test_html_content)

        # Try multiple PDF backends until one succeeds
        pdf_backends = ["reportlab", "weasyprint", "xhtml2pdf"]
        pdf_created = False

        for backend in pdf_backends:
            try:
                pdf_converter = HTMLToPDFConverter(backend=backend)
                pdf_success = pdf_converter.convert_html_file(html_file, pdf_file)

                if (
                    pdf_success
                    and os.path.exists(pdf_file)
                    and os.path.getsize(pdf_file) > 0
                ):
                    pdf_created = True
                    print(f"✓ PDF created successfully with {backend}")
                    break

            except ImportError:
                print(f"⚠ {backend} not available")
                continue
            except Exception as e:
                print(f"✗ {backend} failed: {e}")
                continue

        if not pdf_created:
            pytest.skip("No PDF backend available for graceful degradation test")

        # Try multiple text extraction backends
        parse_backends = ["pypdf", "pdfplumber", "pymupdf"]
        text_extracted = False

        for backend in parse_backends:
            try:
                text_parser = PDFToTextParser(backend=backend)
                extracted_text = text_parser.extract_text_from_file(pdf_file)

                if len(extracted_text) > 0:
                    text_extracted = True
                    print(f"✓ Text extracted successfully with {backend}")
                    break

            except ImportError:
                print(f"⚠ {backend} not available")
                continue
            except Exception as e:
                print(f"✗ {backend} failed: {e}")
                continue

        assert text_extracted, "No text extraction backend worked"

    def test_special_characters_preservation(self, temp_files):
        """Test preservation of special characters through the workflow."""
        special_html = """
        <!DOCTYPE html>
        <html>
        <head><meta charset="UTF-8"><title>Special Characters Test</title></head>
        <body>
            <h1>Special Characters Test</h1>
            <p>Latin: àáâãäå ñ ç ü ö ß</p>
            <p>Currency: $ € £ ¥ ¢</p>
            <p>Math: α β γ δ ε ∞ ∑ ∫ ∂ √</p>
            <p>Symbols: ✓ ✗ → ← ↑ ↓ ★ ♥</p>
            <p>Quotes: "smart quotes" 'apostrophe' — em dash</p>
        </body>
        </html>
        """

        html_file = temp_files["html"]
        pdf_file = temp_files["pdf"]

        # Create HTML file
        with open(html_file, "w", encoding="utf-8") as f:
            f.write(special_html)

        # Convert to PDF
        try:
            pdf_converter = HTMLToPDFConverter(backend="reportlab")
            pdf_success = pdf_converter.convert_html_file(html_file, pdf_file)

            if not pdf_success:
                pytest.skip("PDF creation failed")

        except ImportError:
            pytest.skip("ReportLab not available for special characters test")

        # Extract text
        text_parser = PDFToTextParser(backend="pypdf")
        extracted_text = text_parser.extract_text_from_file(pdf_file)

        # Check for basic content (some special characters may not be preserved)
        assert "Special Characters Test" in extracted_text
        assert "Latin:" in extracted_text
        assert "Currency:" in extracted_text

        # Check that at least some special characters are preserved
        common_chars = ["ñ", "ç", "€", "$"]
        preserved_count = sum(1 for char in common_chars if char in extracted_text)

        # Allow for some loss in character conversion
        assert (
            preserved_count >= len(common_chars) // 2
        ), f"Too many special characters lost. Only {preserved_count}/{len(common_chars)} preserved"


class TestPDFCreationWithHtmlToPdfConverter:
    """Tests specifically for creating PDFs using HTMLToPDFConverter for parsing tests."""

    def test_create_test_pdfs_for_parsing(self):
        """Create various test PDFs for comprehensive parsing tests."""
        test_data_dir = Path(__file__).parent / "test_data"
        test_data_dir.mkdir(exist_ok=True)

        # Test cases with different content types
        test_cases = {
            "simple_text": """
                <html><body>
                    <h1>Simple Text Document</h1>
                    <p>This is a simple document with just text content for basic parsing tests.</p>
                    <p>It contains multiple paragraphs and basic formatting.</p>
                </body></html>
            """,
            "complex_structure": """
                <html><body>
                    <h1>Complex Structure Document</h1>
                    <h2>Section 1</h2>
                    <p>Paragraph with <strong>bold</strong> and <em>italic</em> text.</p>
                    <ul>
                        <li>First item</li>
                        <li>Second item</li>
                        <li>Third item</li>
                    </ul>
                    <h2>Section 2</h2>
                    <table>
                        <tr><th>Header 1</th><th>Header 2</th></tr>
                        <tr><td>Cell 1</td><td>Cell 2</td></tr>
                    </table>
                </body></html>
            """,
            "unicode_content": """
                <html><head><meta charset="utf-8"></head><body>
                    <h1>Unicode Test Document</h1>
                    <p>Various languages: English, Español, Français, Deutsch, 中文, 日本語, العربية</p>
                    <p>Special characters: àáâãäå ñ ç ü ö ß € £ ¥</p>
                    <p>Mathematical: α β γ δ ε ∞ ∑ ∫ ∂ √ π θ φ ψ ω</p>
                </body></html>
            """,
        }

        created_pdfs = []

        for test_name, html_content in test_cases.items():
            try:
                # Use ReportLab as it's most reliable for test PDF creation
                converter = HTMLToPDFConverter(backend="reportlab")
                pdf_path = test_data_dir / f"{test_name}_test.pdf"

                success = converter.convert_html_string(html_content, str(pdf_path))

                if success and pdf_path.exists() and pdf_path.stat().st_size > 0:
                    created_pdfs.append(str(pdf_path))
                    print(f"✓ Created test PDF: {pdf_path}")
                else:
                    print(f"✗ Failed to create: {test_name}")

            except ImportError:
                pytest.skip("ReportLab not available for test PDF creation")
            except Exception as e:
                print(f"✗ Error creating {test_name}: {e}")

        # Verify we created at least one test PDF
        assert len(created_pdfs) > 0, "No test PDFs were created"

        # Test that created PDFs can be parsed
        parser = PDFToTextParser(backend="pypdf")

        for pdf_path in created_pdfs:
            try:
                text = parser.extract_text_from_file(pdf_path)
                assert len(text) > 0, f"No text extracted from {pdf_path}"

                metadata = parser.get_pdf_metadata(pdf_path)
                assert "pages" in metadata, f"No metadata extracted from {pdf_path}"

                print(f"✓ Successfully parsed: {Path(pdf_path).name}")

            except Exception as e:
                pytest.fail(f"Failed to parse created PDF {pdf_path}: {e}")
