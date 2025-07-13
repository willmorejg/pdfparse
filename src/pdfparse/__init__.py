"""PDFParse - A Python package for parsing PDF documents."""

__version__ = "0.1.0"
__author__ = "James G Willmore"
__email__ = "willmorejg@gmail.com"

# Main package imports
from .html_to_pdf import HTMLToPDFConverter
from .pdf_to_text import PDFToTextParser

# Make key classes available at package level
__all__ = [
    "HTMLToPDFConverter",
    "PDFToTextParser",
]
