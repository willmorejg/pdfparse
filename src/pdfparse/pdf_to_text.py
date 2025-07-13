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
PDF to Text Parser

A Python module that extracts text content from PDF files using pure Python libraries.
Supports multiple extraction methods and provides comprehensive text parsing capabilities.
"""

import logging
import re
from pathlib import Path
from typing import Dict, List, Optional, Union

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PDFToTextParser:
    """PDF text extraction class supporting multiple parsing backends."""

    def __init__(self, backend: str = "pypdf"):
        """
        Initialize PDF parser with specified backend.

        Args:
            backend: PDF parsing backend ('pypdf', 'pdfplumber', 'pymupdf')
        """
        self.backend = backend.lower()
        self.validate_backend()
        self._page_cache = {}  # Cache for parsed pages

    def validate_backend(self):
        """Validate that the selected backend is available."""
        supported_backends = ["pypdf", "pdfplumber", "pymupdf"]
        if self.backend not in supported_backends:
            raise ValueError(
                f"Backend '{self.backend}' not supported. Choose from: {supported_backends}"
            )

        # Check if required libraries are installed
        try:
            if self.backend == "pypdf":
                pass
            elif self.backend == "pdfplumber":
                pass
            elif self.backend == "pymupdf":
                import fitz  # PyMuPDF
        except ImportError as e:
            raise ImportError(
                f"Required library for '{self.backend}' backend not found: {e}"
            )

    def extract_text_from_file(
        self, pdf_file: Union[str, Path], pages: Optional[List[int]] = None, **options
    ) -> str:
        """
        Extract text from PDF file.

        Args:
            pdf_file: Path to input PDF file
            pages: List of page numbers to extract (0-indexed), None for all pages
            **options: Backend-specific options

        Returns:
            str: Extracted text content

        Raises:
            FileNotFoundError: If PDF file doesn't exist
            Exception: If PDF parsing fails
        """
        pdf_path = Path(pdf_file)
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_file}")

        if pdf_path.suffix.lower() != ".pdf":
            raise ValueError(f"File must be a PDF: {pdf_file}")

        try:
            if self.backend == "pypdf":
                return self._extract_with_pypdf(pdf_path, pages, **options)
            elif self.backend == "pdfplumber":
                return self._extract_with_pdfplumber(pdf_path, pages, **options)
            elif self.backend == "pymupdf":
                return self._extract_with_pymupdf(pdf_path, pages, **options)
            else:
                raise ValueError(f"Unsupported backend: {self.backend}")
        except Exception as e:
            logger.error(f"Error extracting text from {pdf_file}: {e}")
            raise

    def extract_text_by_page(
        self, pdf_file: Union[str, Path], **options
    ) -> Dict[int, str]:
        """
        Extract text from PDF file, returning text by page.

        Args:
            pdf_file: Path to input PDF file
            **options: Backend-specific options

        Returns:
            Dict[int, str]: Dictionary mapping page numbers (0-indexed) to text content
        """
        pdf_path = Path(pdf_file)
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_file}")

        try:
            if self.backend == "pypdf":
                return self._extract_by_page_pypdf(pdf_path, **options)
            elif self.backend == "pdfplumber":
                return self._extract_by_page_pdfplumber(pdf_path, **options)
            elif self.backend == "pymupdf":
                return self._extract_by_page_pymupdf(pdf_path, **options)
            else:
                raise ValueError(f"Unsupported backend: {self.backend}")
        except Exception as e:
            logger.error(f"Error extracting text by page from {pdf_file}: {e}")
            raise

    def _extract_with_pypdf(
        self, pdf_path: Path, pages: Optional[List[int]] = None, **options
    ) -> str:
        """Extract text using PyPDF backend."""
        import pypdf

        text_content = []

        with open(pdf_path, "rb") as file:
            pdf_reader = pypdf.PdfReader(file)
            total_pages = len(pdf_reader.pages)

            # Determine which pages to process
            if pages is None:
                pages_to_process = range(total_pages)
            else:
                pages_to_process = [p for p in pages if 0 <= p < total_pages]

            for page_num in pages_to_process:
                try:
                    page = pdf_reader.pages[page_num]
                    text = page.extract_text()

                    # Clean extracted text
                    if options.get("clean_text", True):
                        text = self._clean_text(text)

                    if text.strip():
                        text_content.append(f"--- Page {page_num + 1} ---\n{text}")

                except Exception as e:
                    logger.warning(f"Error extracting page {page_num}: {e}")
                    continue

        return "\n\n".join(text_content)

    def _extract_with_pdfplumber(
        self, pdf_path: Path, pages: Optional[List[int]] = None, **options
    ) -> str:
        """Extract text using pdfplumber backend."""
        import pdfplumber

        text_content = []

        with pdfplumber.open(pdf_path) as pdf:
            total_pages = len(pdf.pages)

            # Determine which pages to process
            if pages is None:
                pages_to_process = range(total_pages)
            else:
                pages_to_process = [p for p in pages if 0 <= p < total_pages]

            for page_num in pages_to_process:
                try:
                    page = pdf.pages[page_num]
                    text = page.extract_text()

                    # Clean extracted text
                    if options.get("clean_text", True):
                        text = self._clean_text(text) if text else ""

                    if text and text.strip():
                        text_content.append(f"--- Page {page_num + 1} ---\n{text}")

                except Exception as e:
                    logger.warning(f"Error extracting page {page_num}: {e}")
                    continue

        return "\n\n".join(text_content)

    def _extract_with_pymupdf(
        self, pdf_path: Path, pages: Optional[List[int]] = None, **options
    ) -> str:
        """Extract text using PyMuPDF backend."""
        import fitz  # PyMuPDF

        text_content = []

        pdf_document = fitz.open(pdf_path)
        total_pages = pdf_document.page_count

        try:
            # Determine which pages to process
            if pages is None:
                pages_to_process = range(total_pages)
            else:
                pages_to_process = [p for p in pages if 0 <= p < total_pages]

            for page_num in pages_to_process:
                try:
                    page = pdf_document[page_num]
                    text = page.get_text()

                    # Clean extracted text
                    if options.get("clean_text", True):
                        text = self._clean_text(text)

                    if text.strip():
                        text_content.append(f"--- Page {page_num + 1} ---\n{text}")

                except Exception as e:
                    logger.warning(f"Error extracting page {page_num}: {e}")
                    continue

        finally:
            pdf_document.close()

        return "\n\n".join(text_content)

    def _extract_by_page_pypdf(self, pdf_path: Path, **options) -> Dict[int, str]:
        """Extract text by page using PyPDF backend."""
        import pypdf

        page_texts = {}

        with open(pdf_path, "rb") as file:
            pdf_reader = pypdf.PdfReader(file)

            for page_num, page in enumerate(pdf_reader.pages):
                try:
                    text = page.extract_text()

                    if options.get("clean_text", True):
                        text = self._clean_text(text)

                    page_texts[page_num] = text

                except Exception as e:
                    logger.warning(f"Error extracting page {page_num}: {e}")
                    page_texts[page_num] = ""

        return page_texts

    def _extract_by_page_pdfplumber(self, pdf_path: Path, **options) -> Dict[int, str]:
        """Extract text by page using pdfplumber backend."""
        import pdfplumber

        page_texts = {}

        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages):
                try:
                    text = page.extract_text()

                    if options.get("clean_text", True):
                        text = self._clean_text(text) if text else ""

                    page_texts[page_num] = text or ""

                except Exception as e:
                    logger.warning(f"Error extracting page {page_num}: {e}")
                    page_texts[page_num] = ""

        return page_texts

    def _extract_by_page_pymupdf(self, pdf_path: Path, **options) -> Dict[int, str]:
        """Extract text by page using PyMuPDF backend."""
        import fitz  # PyMuPDF

        page_texts = {}

        pdf_document = fitz.open(pdf_path)

        try:
            for page_num in range(pdf_document.page_count):
                try:
                    page = pdf_document[page_num]
                    text = page.get_text()

                    if options.get("clean_text", True):
                        text = self._clean_text(text)

                    page_texts[page_num] = text

                except Exception as e:
                    logger.warning(f"Error extracting page {page_num}: {e}")
                    page_texts[page_num] = ""

        finally:
            pdf_document.close()

        return page_texts

    def _clean_text(self, text: str) -> str:
        """
        Clean extracted text by removing extra whitespace and formatting issues.

        Args:
            text: Raw extracted text

        Returns:
            str: Cleaned text
        """
        if not text:
            return ""

        # Remove excessive whitespace
        text = re.sub(r"\s+", " ", text)

        # Remove leading/trailing whitespace
        text = text.strip()

        # Fix common formatting issues
        text = re.sub(r"([.!?])\s*([A-Z])", r"\1 \2", text)  # Space after sentences
        text = re.sub(r"([a-z])([A-Z])", r"\1 \2", text)  # Space between words

        return text

    def get_pdf_metadata(self, pdf_file: Union[str, Path]) -> Dict[str, str]:
        """
        Extract metadata from PDF file.

        Args:
            pdf_file: Path to PDF file

        Returns:
            Dict[str, str]: PDF metadata
        """
        pdf_path = Path(pdf_file)
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_file}")

        metadata = {}

        try:
            if self.backend == "pypdf":
                import pypdf

                with open(pdf_path, "rb") as file:
                    pdf_reader = pypdf.PdfReader(file)
                    if pdf_reader.metadata:
                        for key, value in pdf_reader.metadata.items():
                            # Remove leading slash from metadata keys
                            clean_key = key.lstrip("/")
                            metadata[clean_key] = str(value) if value else ""
                    metadata["pages"] = str(len(pdf_reader.pages))

            elif self.backend == "pdfplumber":
                import pdfplumber

                with pdfplumber.open(pdf_path) as pdf:
                    if pdf.metadata:
                        for key, value in pdf.metadata.items():
                            metadata[key] = str(value) if value else ""
                    metadata["pages"] = str(len(pdf.pages))

            elif self.backend == "pymupdf":
                import fitz

                pdf_document = fitz.open(pdf_path)
                try:
                    metadata = pdf_document.metadata
                    metadata["pages"] = str(pdf_document.page_count)
                finally:
                    pdf_document.close()

        except Exception as e:
            logger.warning(f"Error extracting metadata from {pdf_file}: {e}")

        return metadata

    def search_text(
        self, pdf_file: Union[str, Path], query: str, case_sensitive: bool = False
    ) -> List[Dict[str, Union[int, str]]]:
        """
        Search for text in PDF file.

        Args:
            pdf_file: Path to PDF file
            query: Text to search for
            case_sensitive: Whether search should be case sensitive

        Returns:
            List[Dict]: List of matches with page numbers and context
        """
        page_texts = self.extract_text_by_page(pdf_file)
        matches = []

        flags = 0 if case_sensitive else re.IGNORECASE
        pattern = re.compile(re.escape(query), flags)

        for page_num, text in page_texts.items():
            if not text:
                continue

            for match in pattern.finditer(text):
                start = max(0, match.start() - 50)
                end = min(len(text), match.end() + 50)
                context = text[start:end].strip()

                matches.append(
                    {
                        "page": page_num + 1,  # 1-indexed for user display
                        "position": match.start(),
                        "context": context,
                        "match": match.group(),
                    }
                )

        return matches
