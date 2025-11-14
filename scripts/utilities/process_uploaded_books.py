"""
Process uploaded books that are waiting in storage/uploads/

Manually triggers BookIngestionAgent for each uploaded PDF.
"""

import sys
import io
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from backend.kernels.agents.book_ingestion_agent import get_book_ingestion_agent


async def process_all_uploads():
    """Process all PDFs in storage/uploads/"""
    
    upload_dir = Path("storage/uploads")
    pdfs = list(upload_dir.glob("*.pdf"))
    
    print(f"\n📚 Found {len(pdfs)} PDFs to process\n")
    print("="*60)
    
    agent = get_book_ingestion_agent()
    await agent.activate()
    
    for i, pdf in enumerate(pdfs, 1):
        print(f"\n[{i}/{len(pdfs)}] Processing: {pdf.name}")
        print("-"*60)
        
        # Extract title from filename
        # Format: 20251113_182116_original-name.pdf
        parts = pdf.stem.split("_", 2)
        original_name = parts[2] if len(parts) > 2 else pdf.stem
        
        # Clean up title
        title = original_name.split("-", 1)[-1] if "-" in original_name else original_name
        title = title.replace("-", " ").replace("_", " ")
        
        metadata = {
            "title": title,
            "author": "Business Intelligence",
            "source_type": "book",
            "trust_level": "high"
        }
        
        print(f"   Title: {title}")
        print(f"   Size: {pdf.stat().st_size / 1024:.1f} KB")
        
        try:
            result = await agent.process_book(pdf, metadata)
            
            print(f"   ✅ Status: {result['status']}")
            print(f"   📄 Document ID: {result.get('document_id', 'N/A')}")
            print(f"   📊 Chunks: {result.get('chunks_created', 0)}")
            print(f"   💡 Insights: {result.get('insights_created', 0)}")
            
            if result.get('errors'):
                print(f"   ⚠️ Errors: {result['errors']}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*60)
    print("✅ PROCESSING COMPLETE")
    print("="*60)
    print("\nCheck results:")
    print("  python query_book.py")
    print()


if __name__ == "__main__":
    asyncio.run(process_all_uploads())
