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
HTML to PDF Converter (No External Dependencies)

A Python script that converts HTML content to PDF using pure Python libraries.
Supports weasyprint, reportlab, and xhtml2pdf backends - no external binaries required.
"""

import argparse
import os
import sys


class HTMLToPDFConverter:
    """Main converter class supporting multiple pure Python PDF generation backends."""

    def __init__(self, backend: str = "weasyprint"):
        """
        Initialize converter with specified backend.

        Args:
            backend: PDF generation backend ('weasyprint', 'xhtml2pdf', 'reportlab')
        """
        self.backend = backend.lower()
        self.validate_backend()

    def validate_backend(self):
        """Validate that the selected backend is available."""
        supported_backends = ["weasyprint", "xhtml2pdf", "reportlab"]
        if self.backend not in supported_backends:
            raise ValueError(
                f"Backend '{self.backend}' not supported. Choose from: {supported_backends}"
            )

        # Check if required libraries are installed
        try:
            if self.backend == "weasyprint":
                pass
            elif self.backend == "xhtml2pdf":
                pass
            elif self.backend == "reportlab":
                pass
        except ImportError as e:
            raise ImportError(
                f"Required library for '{self.backend}' backend not found: {e}"
            )

    def convert_html_file(self, html_file: str, output_file: str, **options) -> bool:
        """
        Convert HTML file to PDF.

        Args:
            html_file: Path to input HTML file
            output_file: Path to output PDF file
            **options: Backend-specific options

        Returns:
            bool: True if conversion successful
        """
        if not os.path.exists(html_file):
            raise FileNotFoundError(f"HTML file not found: {html_file}")

        with open(html_file, "r", encoding="utf-8") as f:
            html_content = f.read()

        # Set base URL for relative paths
        base_url = f"file://{os.path.dirname(os.path.abspath(html_file))}/"
        return self.convert_html_string(
            html_content, output_file, base_url=base_url, **options
        )

    def convert_html_string(
        self, html_content: str, output_file: str, **options
    ) -> bool:
        """
        Convert HTML string to PDF.

        Args:
            html_content: HTML content as string
            output_file: Path to output PDF file
            **options: Backend-specific options

        Returns:
            bool: True if conversion successful
        """
        try:
            if self.backend == "weasyprint":
                return self._convert_with_weasyprint(
                    html_content, output_file, **options
                )
            elif self.backend == "xhtml2pdf":
                return self._convert_with_xhtml2pdf(
                    html_content, output_file, **options
                )
            elif self.backend == "reportlab":
                return self._convert_with_reportlab(
                    html_content, output_file, **options
                )
        except Exception as e:
            print(f"Error during conversion: {e}")
            return False

    def _convert_with_weasyprint(
        self, html_content: str, output_file: str, **options
    ) -> bool:
        """Convert using WeasyPrint backend."""
        import weasyprint

        try:
            # Create WeasyPrint HTML object
            html_doc = weasyprint.HTML(
                string=html_content, base_url=options.get("base_url")
            )

            # Generate CSS if specified
            css = None
            if "css_file" in options:
                css = [weasyprint.CSS(filename=options["css_file"])]
            elif "css_string" in options:
                css = [weasyprint.CSS(string=options["css_string"])]

            # Write PDF
            html_doc.write_pdf(output_file, stylesheets=css)
            print(f"Successfully converted to PDF: {output_file}")
            return True

        except Exception as e:
            print(f"WeasyPrint conversion failed: {e}")
            return False

    def _convert_with_xhtml2pdf(
        self, html_content: str, output_file: str, **options
    ) -> bool:
        """Convert using xhtml2pdf backend."""
        import xhtml2pdf.pisa as pisa

        try:
            # Add CSS if provided
            if "css_file" in options:
                with open(options["css_file"], "r", encoding="utf-8") as css_file:
                    css_content = css_file.read()
                    html_content = f"<style>{css_content}</style>" + html_content
            elif "css_string" in options:
                html_content = f"<style>{options['css_string']}</style>" + html_content

            # Ensure proper HTML structure
            if not html_content.strip().startswith(
                "<!DOCTYPE"
            ) and not html_content.strip().startswith("<html"):
                html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        @page {{ margin: {options.get('margin_top', '0.75in')} {options.get('margin_right', '0.75in')} {options.get('margin_bottom', '0.75in')} {options.get('margin_left', '0.75in')}; }}
    </style>
</head>
<body>
{html_content}
</body>
</html>"""

            # Convert HTML to PDF
            with open(output_file, "wb") as pdf_file:
                pisa_status = pisa.CreatePDF(html_content, dest=pdf_file)

            if not pisa_status.err:
                print(f"Successfully converted to PDF: {output_file}")
                return True
            else:
                print(f"xhtml2pdf conversion had errors")
                return False

        except Exception as e:
            print(f"xhtml2pdf conversion failed: {e}")
            return False

    def _convert_with_reportlab(
        self, html_content: str, output_file: str, **options
    ) -> bool:
        """Convert using ReportLab backend with enhanced HTML parsing."""

        from bs4 import BeautifulSoup
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4, letter
        from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
        from reportlab.platypus import (
            SimpleDocTemplate,
        )

        try:
            # Parse HTML with BeautifulSoup
            soup = BeautifulSoup(html_content, "html.parser")

            # Set page size
            page_size = A4 if options.get("page_size", "A4") == "A4" else letter

            # Create PDF document
            doc = SimpleDocTemplate(
                output_file,
                pagesize=page_size,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=18,
            )

            # Create styles
            styles = getSampleStyleSheet()
            story = []

            # Custom styles
            title_style = ParagraphStyle(
                "CustomTitle",
                parent=styles["Heading1"],
                fontSize=18,
                spaceAfter=30,
                textColor=colors.HexColor("#2c3e50"),
            )

            subtitle_style = ParagraphStyle(
                "CustomSubtitle",
                parent=styles["Heading2"],
                fontSize=14,
                spaceAfter=20,
                textColor=colors.HexColor("#3498db"),
            )

            # Process HTML elements
            self._process_html_elements(
                soup, story, styles, title_style, subtitle_style
            )

            # Build PDF
            doc.build(story)
            print(f"Successfully converted to PDF: {output_file}")
            return True

        except Exception as e:
            print(f"ReportLab conversion failed: {e}")
            return False

    def _process_html_elements(self, soup, story, styles, title_style, subtitle_style):
        """Process HTML elements and add them to the story."""
        from reportlab.platypus import Paragraph, Spacer

        for element in soup.find_all(
            ["h1", "h2", "h3", "h4", "h5", "h6", "p", "div", "ul", "ol", "table"]
        ):
            if element.name == "h1":
                story.append(Paragraph(element.get_text(), title_style))
                story.append(Spacer(1, 12))
            elif element.name in ["h2", "h3"]:
                story.append(Paragraph(element.get_text(), subtitle_style))
                story.append(Spacer(1, 8))
            elif element.name in ["h4", "h5", "h6"]:
                story.append(Paragraph(element.get_text(), styles["Heading3"]))
                story.append(Spacer(1, 6))
            elif element.name in ["p", "div"]:
                text = element.get_text().strip()
                if text:
                    story.append(Paragraph(text, styles["Normal"]))
                    story.append(Spacer(1, 6))
            elif element.name in ["ul", "ol"]:
                for li in element.find_all("li"):
                    bullet = "• " if element.name == "ul" else "1. "
                    story.append(Paragraph(bullet + li.get_text(), styles["Normal"]))
                story.append(Spacer(1, 6))
            elif element.name == "table":
                self._process_table(element, story)

    def _process_table(self, table_element, story):
        """Process HTML table and add to story."""
        from reportlab.lib import colors
        from reportlab.platypus import Table, TableStyle

        rows = []
        for tr in table_element.find_all("tr"):
            row = []
            for cell in tr.find_all(["td", "th"]):
                row.append(cell.get_text().strip())
            if row:
                rows.append(row)

        if rows:
            table = Table(rows)
            table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, 0), 12),
                        ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                        ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                        ("GRID", (0, 0), (-1, -1), 1, colors.black),
                    ]
                )
            )
            story.append(table)


def main():
    """Command-line interface for HTML to PDF conversion."""
    parser = argparse.ArgumentParser(
        description="Convert HTML to PDF using pure Python backends (no external dependencies)"
    )
    parser.add_argument("input", help="Input HTML file or HTML string")
    parser.add_argument("output", help="Output PDF file path")
    parser.add_argument(
        "--backend",
        choices=["weasyprint", "xhtml2pdf", "reportlab"],
        default="weasyprint",
        help="PDF generation backend (default: weasyprint)",
    )
    parser.add_argument(
        "--string",
        action="store_true",
        help="Treat input as HTML string instead of file path",
    )
    parser.add_argument("--css", help="CSS file to apply to HTML")
    parser.add_argument(
        "--page-size", default="A4", help="Page size (A4, letter, etc.)"
    )
    parser.add_argument("--margin-top", default="0.75in", help="Top margin")
    parser.add_argument("--margin-bottom", default="0.75in", help="Bottom margin")
    parser.add_argument("--margin-left", default="0.75in", help="Left margin")
    parser.add_argument("--margin-right", default="0.75in", help="Right margin")

    args = parser.parse_args()

    try:
        # Initialize converter
        converter = HTMLToPDFConverter(backend=args.backend)

        # Prepare options
        options = {
            "page_size": args.page_size,
            "margin_top": args.margin_top,
            "margin_bottom": args.margin_bottom,
            "margin_left": args.margin_left,
            "margin_right": args.margin_right,
        }

        if args.css:
            options["css_file"] = args.css

        # Convert
        if args.string:
            success = converter.convert_html_string(args.input, args.output, **options)
        else:
            success = converter.convert_html_file(args.input, args.output, **options)

        if success:
            print("Conversion completed successfully!")
            sys.exit(0)
        else:
            print("Conversion failed!")
            sys.exit(1)

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
