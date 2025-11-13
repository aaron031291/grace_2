"""
Simple PDF book ingestion - finds PDFs and ingests them
"""

import sys
import io
import os
import glob

# Fix encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("Finding PDF files...")

# Search for PDFs in common locations
search_paths = [
    "business intelligence/*.pdf",
    "../business intelligence/*.pdf",
    "../../business intelligence/*.pdf",
    os.path.expanduser("~/Documents/**/business intelligence/*.pdf"),
    "*.pdf"  # Current directory as fallback
]

found_pdfs = []
for pattern in search_paths:
    pdfs = glob.glob(pattern, recursive=True)
    if pdfs:
        found_pdfs.extend(pdfs)
        print(f"Found {len(pdfs)} PDFs in pattern: {pattern}")

if not found_pdfs:
    print("\nNo PDFs found. Please provide the full path:")
    print("Example: python ingest_books_simple.py 'C:\\path\\to\\business intelligence'")
    
    if len(sys.argv) > 1:
        custom_path = sys.argv[1]
        pattern = os.path.join(custom_path, "*.pdf")
        found_pdfs = glob.glob(pattern)
        if found_pdfs:
            print(f"\nFound {len(found_pdfs)} PDFs in {custom_path}")
        else:
            print(f"\nNo PDFs found in {custom_path}")
            sys.exit(1)
    else:
        sys.exit(1)

# Remove duplicates
found_pdfs = list(set(found_pdfs))

print(f"\n📚 Total PDFs found: {len(found_pdfs)}\n")

for i, pdf in enumerate(found_pdfs[:20], 1):  # Show first 20
    filename = os.path.basename(pdf)
    size_kb = os.path.getsize(pdf) / 1024
    print(f"{i}. {filename} ({size_kb:.1f} KB)")

if len(found_pdfs) > 20:
    print(f"... and {len(found_pdfs) - 20} more")

print(f"\n\nTo ingest these files, use:")
pdf_dir = os.path.dirname(found_pdfs[0]) if found_pdfs else "."
print(f'python scripts/ingest_pdf_batch.py "{pdf_dir}"')
