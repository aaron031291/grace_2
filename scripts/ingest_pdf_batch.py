"""
Batch PDF Ingestion for Grace

Ingests multiple PDFs from a directory into Grace's knowledge base.
Handles PDF text extraction, chunking, embedding, and storage.
"""

import sys
import io
import os
import requests
import time
from pathlib import Path
from typing import List, Dict, Any

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

BASE_URL = "http://localhost:8000"


class PDFBatchIngester:
    def __init__(self, directory: str, base_url: str = BASE_URL):
        self.directory = Path(directory)
        self.base_url = base_url
        self.results = []
        
    def find_pdfs(self) -> List[Path]:
        """Find all PDF files in directory"""
        if not self.directory.exists():
            print(f"❌ Directory not found: {self.directory}")
            return []
        
        pdfs = list(self.directory.glob("*.pdf"))
        print(f"\n📚 Found {len(pdfs)} PDF files in {self.directory}\n")
        return pdfs
    
    def extract_metadata(self, filepath: Path) -> Dict[str, Any]:
        """Extract basic metadata from filename"""
        filename = filepath.stem
        
        # Try to parse title and author from filename
        # Common patterns: "Author-Title.pdf" or "Title-by-Author.pdf"
        title = filename.replace("-", " ").replace("_", " ")
        
        # Clean up common patterns
        title = title.replace(".pdf", "")
        
        # Extract author if present
        author = "Unknown"
        if " by " in title.lower():
            parts = title.split(" by ")
            title = parts[0].strip()
            author = parts[1].strip()
        elif "-" in filename and len(filename.split("-")) > 1:
            # Might be Author-Title format
            parts = filename.split("-", 1)
            if len(parts[0]) < 50:  # Reasonable author name length
                author = parts[0].strip()
                title = parts[1].replace(".pdf", "").strip()
        
        return {
            "title": title,
            "author": author,
            "filename": filepath.name,
            "size_kb": filepath.stat().st_size / 1024,
            "filepath": str(filepath)
        }
    
    def upload_pdf(self, filepath: Path, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Upload single PDF to Grace"""
        print(f"\n{'='*60}")
        print(f"📖 Processing: {metadata['title']}")
        print(f"   Author: {metadata['author']}")
        print(f"   Size: {metadata['size_kb']:.1f} KB")
        print(f"{'='*60}")
        
        try:
            # Check if file exists
            if not filepath.exists():
                return {
                    "success": False,
                    "error": "File not found",
                    "metadata": metadata
                }
            
            # Prepare upload
            files = {
                "file": (filepath.name, open(filepath, "rb"), "application/pdf")
            }
            
            data = {
                "title": metadata["title"],
                "author": metadata["author"],
                "source": "business_intelligence",
                "trust_level": "high"
            }
            
            # Upload
            print("⬆️ Uploading...")
            response = requests.post(
                f"{self.base_url}/api/books/upload",
                files=files,
                data=data,
                timeout=300  # 5 minute timeout for large PDFs
            )
            
            files["file"][1].close()  # Close file
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Upload successful!")
                print(f"   Document ID: {result.get('document_id', 'N/A')}")
                print(f"   Status: {result.get('status', 'N/A')}")
                
                return {
                    "success": True,
                    "metadata": metadata,
                    "response": result
                }
            else:
                print(f"❌ Upload failed: {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}",
                    "metadata": metadata,
                    "response_text": response.text[:500]
                }
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return {
                "success": False,
                "error": str(e),
                "metadata": metadata
            }
    
    def ingest_all(self, delay_between: int = 5) -> Dict[str, Any]:
        """Ingest all PDFs with delay between uploads"""
        pdfs = self.find_pdfs()
        
        if not pdfs:
            return {
                "success": False,
                "total": 0,
                "processed": 0,
                "failed": 0
            }
        
        total = len(pdfs)
        successful = 0
        failed = 0
        
        print(f"\n🚀 Starting batch ingestion of {total} PDFs...")
        print(f"⏱️ Delay between uploads: {delay_between} seconds\n")
        
        for i, pdf in enumerate(pdfs, 1):
            print(f"\n[{i}/{total}] Processing {pdf.name}...")
            
            metadata = self.extract_metadata(pdf)
            result = self.upload_pdf(pdf, metadata)
            
            self.results.append(result)
            
            if result["success"]:
                successful += 1
            else:
                failed += 1
            
            # Delay between uploads (except after last one)
            if i < total:
                print(f"\n⏸️ Waiting {delay_between} seconds before next upload...")
                time.sleep(delay_between)
        
        # Summary
        print("\n" + "="*60)
        print("BATCH INGESTION COMPLETE")
        print("="*60)
        print(f"✅ Successful: {successful}/{total}")
        print(f"❌ Failed: {failed}/{total}")
        
        if failed > 0:
            print(f"\n⚠️ Failed uploads:")
            for result in self.results:
                if not result["success"]:
                    print(f"   - {result['metadata']['title']}: {result.get('error', 'Unknown error')}")
        
        return {
            "success": failed == 0,
            "total": total,
            "successful": successful,
            "failed": failed,
            "results": self.results
        }
    
    def check_system_status(self):
        """Check if Grace is ready"""
        print("\n🔍 Checking system status...")
        
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                print("✅ Backend is healthy")
                return True
            else:
                print(f"❌ Backend returned {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Cannot reach backend: {e}")
            print("\n⚠️ Make sure the backend is running:")
            print("   python serve.py")
            return False


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("\n❌ Usage: python ingest_pdf_batch.py <directory>")
        print("\nExample:")
        print("  python ingest_pdf_batch.py \"business intelligence\"")
        print("  python ingest_pdf_batch.py txt/business_books")
        print("\nOptions:")
        print("  --delay <seconds>    Delay between uploads (default: 5)")
        print()
        sys.exit(1)
    
    directory = sys.argv[1]
    delay = 5
    
    # Parse delay option
    if "--delay" in sys.argv:
        try:
            delay_idx = sys.argv.index("--delay")
            delay = int(sys.argv[delay_idx + 1])
        except (IndexError, ValueError):
            print("⚠️ Invalid --delay value, using default (5 seconds)")
    
    print("\n" + "="*60)
    print("GRACE PDF BATCH INGESTION")
    print("="*60)
    print(f"Directory: {directory}")
    print(f"Delay: {delay} seconds between uploads")
    print("="*60)
    
    ingester = PDFBatchIngester(directory)
    
    # Check system
    if not ingester.check_system_status():
        sys.exit(1)
    
    # Find PDFs
    pdfs = ingester.find_pdfs()
    if not pdfs:
        sys.exit(1)
    
    # Confirm
    print("\n📋 Files to ingest:")
    for i, pdf in enumerate(pdfs, 1):
        metadata = ingester.extract_metadata(pdf)
        print(f"   {i}. {metadata['title']}")
        print(f"      ({metadata['size_kb']:.1f} KB)")
    
    print("\n⚠️ This will upload and process all PDFs above.")
    response = input("\nContinue? (y/N): ")
    
    if response.lower() != 'y':
        print("❌ Cancelled by user")
        sys.exit(0)
    
    # Ingest
    result = ingester.ingest_all(delay_between=delay)
    
    # Final status
    if result["success"]:
        print("\n🎉 All PDFs ingested successfully!")
        print("\nNext steps:")
        print("  1. Check status: curl http://localhost:8000/api/books/stats")
        print("  2. View books: python query_book.py")
        print("  3. Search knowledge: python query_book.py \"marketing\"")
    else:
        print(f"\n⚠️ {result['failed']} PDFs failed to ingest")
        print("Check the errors above and try again")
        sys.exit(1)


if __name__ == "__main__":
    main()
