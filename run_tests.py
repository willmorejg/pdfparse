#!/usr/bin/env python3
"""
Test runner script for pdfparse HTML to PDF conversion.

This script demonstrates the testing capabilities and shows
how the HTML to PDF conversion works with different backends.
"""

import sys
import subprocess
from pathlib import Path

def main():
    """Run tests and demonstrate functionality."""
    print("🧪 PDFParse HTML to PDF Converter - Test Suite")
    print("=" * 50)
    
    # Change to project root directory
    project_root = Path(__file__).parent
    
    print("\n📋 Running comprehensive test suite...")
    result = subprocess.run([
        sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short"
    ], cwd=project_root, check=False)
    
    if result.returncode == 0:
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Some tests failed!")
        return 1
    
    print("\n📊 Running tests with coverage report...")
    subprocess.run([
        sys.executable, "-m", "pytest", "tests/", 
        "--cov=src/pdfparse", "--cov-report=term-missing"
    ], cwd=project_root, check=False)
    
    print("\n📁 Generated PDF files in tests/test_data/:")
    test_data = project_root / "tests" / "test_data"
    for pdf_file in test_data.glob("*.pdf"):
        size_kb = pdf_file.stat().st_size / 1024
        print(f"  • {pdf_file.name} ({size_kb:.1f} KB)")
    
    print("\n🎯 Test Summary:")
    print("  • HTML file parsing and validation")
    print("  • PDF generation with WeasyPrint backend")
    print("  • PDF generation with xhtml2pdf backend") 
    print("  • PDF generation with ReportLab backend")
    print("  • Error handling and edge cases")
    print("  • Command-line interface testing")
    print("  • Integration workflow testing")
    
    print("\n✨ Test suite completed successfully!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
