"""Command-line interface for pdfparse."""

import click


@click.command()
@click.version_option()
def main():
    """PDFParse - A Python package for parsing PDF documents."""
    click.echo("PDFParse CLI - Coming soon!")


if __name__ == "__main__":
    main()
