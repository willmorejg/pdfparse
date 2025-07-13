#!/usr/bin/env python3
"""
Script to create test PDF files for testing PDF text extraction
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

    def create_test_pdf():
        """Create a test PDF file for testing text extraction."""
        # Create test directory if it doesn't exist
        test_dir = Path(__file__).parent / "test_data"
        test_dir.mkdir(exist_ok=True)

        # Create test PDF
        pdf_file = test_dir / "sample_document.pdf"
        doc = SimpleDocTemplate(str(pdf_file), pagesize=letter)
        styles = getSampleStyleSheet()
        story = []

        # Add content
        story.append(Paragraph("PDF Parser Test Document", styles["Title"]))
        story.append(Spacer(1, 12))
        story.append(Paragraph("Introduction", styles["Heading1"]))
        story.append(
            Paragraph(
                "This is a test document created specifically for testing PDF text extraction capabilities.",
                styles["Normal"],
            )
        )
        story.append(Spacer(1, 12))
        story.append(Paragraph("Features to Test", styles["Heading1"]))
        story.append(Paragraph("• Basic text extraction", styles["Normal"]))
        story.append(Paragraph("• Header recognition", styles["Normal"]))
        story.append(Paragraph("• Multi-page documents", styles["Normal"]))
        story.append(Spacer(1, 12))
        story.append(Paragraph("Search Test Content", styles["Heading1"]))
        story.append(
            Paragraph(
                "This paragraph contains the word searchable which can be used to test text search functionality. The word appears multiple times: searchable content, searchable text, and searchable documents.",
                styles["Normal"],
            )
        )
        story.append(Spacer(1, 12))
        story.append(Paragraph("Numbers and Special Characters", styles["Heading1"]))
        story.append(
            Paragraph(
                "Testing numbers: 12345, dates: 2025-07-13, and special characters: àáâãäå",
                styles["Normal"],
            )
        )

        # Build PDF
        doc.build(story)
        print(f"Created test PDF: {pdf_file}")

        if pdf_file.exists():
            print(f"File size: {pdf_file.stat().st_size} bytes")
            return True
        else:
            print("PDF file was not created")
            return False

    if __name__ == "__main__":
        create_test_pdf()

except Exception as e:
    print(f"Error: {e}")
    import traceback

    traceback.print_exc()
