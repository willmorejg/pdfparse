"""Command-line interface for pdfparse."""

import sys

import click

from .html_to_pdf import HTMLToPDFConverter
from .pdf_to_text import PDFToTextParser


@click.group()
@click.version_option()
def main():
    """PDFParse - A Python package for parsing PDF documents."""


@main.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.argument("output_file", type=click.Path())
@click.option(
    "--backend",
    type=click.Choice(["weasyprint", "xhtml2pdf", "reportlab"]),
    default="weasyprint",
    help="PDF generation backend",
)
@click.option("--css", type=click.Path(exists=True), help="CSS file to apply")
@click.option("--page-size", default="A4", help="Page size (A4, letter, etc.)")
def html2pdf(input_file, output_file, backend, css, page_size):
    """Convert HTML file to PDF."""
    try:
        converter = HTMLToPDFConverter(backend=backend)

        options = {"page_size": page_size}
        if css:
            options["css_file"] = css

        success = converter.convert_html_file(input_file, output_file, **options)

        if success:
            click.echo(f"Successfully converted {input_file} to {output_file}")
        else:
            click.echo("Conversion failed!", err=True)
            sys.exit(1)

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.argument("pdf_file", type=click.Path(exists=True))
@click.option(
    "--output", "-o", type=click.Path(), help="Output text file (default: stdout)"
)
@click.option(
    "--backend",
    type=click.Choice(["pypdf", "pdfplumber", "pymupdf"]),
    default="pypdf",
    help="PDF parsing backend",
)
@click.option("--pages", help='Specific pages to extract (e.g., "1,3,5" or "1-5")')
@click.option("--search", help="Search for specific text in the PDF")
@click.option("--metadata", is_flag=True, help="Extract and display metadata only")
def pdf2text(pdf_file, output, backend, pages, search, metadata):
    """Extract text from PDF file."""
    try:
        parser = PDFToTextParser(backend=backend)

        if metadata:
            # Extract and display metadata
            meta = parser.get_pdf_metadata(pdf_file)
            click.echo("PDF Metadata:")
            for key, value in meta.items():
                click.echo(f"  {key}: {value}")
            return

        if search:
            # Search for text
            matches = parser.search_text(pdf_file, search)
            if matches:
                click.echo(f"Found {len(matches)} matches for '{search}':")
                for match in matches:
                    click.echo(f"  Page {match['page']}: {match['context']}")
            else:
                click.echo(f"No matches found for '{search}'")
            return

        # Parse pages parameter if provided
        page_list = None
        if pages:
            try:
                if "-" in pages:
                    start, end = map(int, pages.split("-"))
                    page_list = list(range(start - 1, end))  # Convert to 0-indexed
                else:
                    page_list = [
                        int(p) - 1 for p in pages.split(",")
                    ]  # Convert to 0-indexed
            except ValueError:
                click.echo("Invalid pages format. Use '1,3,5' or '1-5'", err=True)
                sys.exit(1)

        # Extract text
        text = parser.extract_text_from_file(pdf_file, pages=page_list)

        if output:
            with open(output, "w", encoding="utf-8") as f:
                f.write(text)
            click.echo(f"Text extracted to {output}")
        else:
            click.echo(text)

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.argument("pdf_file", type=click.Path(exists=True))
@click.argument("query")
@click.option("--case-sensitive", is_flag=True, help="Case sensitive search")
def search(pdf_file, query, case_sensitive):
    """Search for text in PDF file."""
    try:
        parser = PDFToTextParser()
        matches = parser.search_text(pdf_file, query, case_sensitive=case_sensitive)

        if matches:
            click.echo(f"Found {len(matches)} matches for '{query}':")
            for match in matches:
                click.echo(f"  Page {match['page']}, position {match['position']}:")
                click.echo(f"    {match['context']}")
        else:
            click.echo(f"No matches found for '{query}'")

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
