#!/usr/bin/env python3
"""
Extract and analyze API data from public-apis-master.zip
"""

import zipfile
import os
import json
import re
from pathlib import Path
from typing import List, Dict, Any

def extract_apis_from_zip(zip_path: str) -> Dict[str, Any]:
    """Extract API data from the zip file"""
    
    results = {
        'total_files': 0,
        'markdown_files': [],
        'api_data': [],
        'ml_ai_apis': [],
        'categories': set()
    }
    
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        # List all files
        file_list = zip_ref.namelist()
        results['total_files'] = len(file_list)
        
        print(f"[FOUND] {len(file_list)} files in zip")
        
        # Find markdown files (likely README with API list)
        for file_name in file_list:
            if file_name.endswith('.md') and not file_name.endswith('CONTRIBUTING.md'):
                results['markdown_files'].append(file_name)
                print(f"[MARKDOWN] Found: {file_name}")
                
                # Extract and parse markdown
                try:
                    content = zip_ref.read(file_name).decode('utf-8')
                    apis = parse_api_table(content)
                    results['api_data'].extend(apis)
                    
                    # Filter ML/AI APIs
                    ml_apis = [api for api in apis if is_ml_related(api)]
                    results['ml_ai_apis'].extend(ml_apis)
                    
                    # Track categories
                    for api in apis:
                        if api.get('category'):
                            results['categories'].add(api['category'])
                            
                except Exception as e:
                    print(f"[WARNING] Error parsing {file_name}: {e}")
    
    results['categories'] = sorted(list(results['categories']))
    return results


def parse_api_table(markdown_content: str) -> List[Dict[str, Any]]:
    """Parse markdown table format to extract API information"""
    
    apis = []
    current_category = None
    
    # Pattern for category headers (### Category Name)
    category_pattern = re.compile(r'^###\s+(.+)$', re.MULTILINE)
    
    # Pattern for table rows
    # | [API Name](url) | Description | Auth | HTTPS | CORS |
    table_row_pattern = re.compile(
        r'\|\s*\[([^\]]+)\]\(([^\)]+)\)\s*\|\s*([^|]+?)\s*\|\s*`?([^|`]+?)`?\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|'
    )
    
    lines = markdown_content.split('\n')
    
    for line in lines:
        # Check for category
        category_match = category_pattern.match(line.strip())
        if category_match:
            current_category = category_match.group(1).strip()
            continue
        
        # Check for table row
        row_match = table_row_pattern.match(line)
        if row_match:
            api = {
                'name': row_match.group(1).strip(),
                'url': row_match.group(2).strip(),
                'description': row_match.group(3).strip(),
                'auth': row_match.group(4).strip(),
                'https': row_match.group(5).strip(),
                'cors': row_match.group(6).strip(),
                'category': current_category
            }
            apis.append(api)
    
    return apis


def is_ml_related(api: Dict[str, Any]) -> bool:
    """Check if API is ML/AI related"""
    
    ml_keywords = [
        'machine learning', 'ml', 'ai', 'artificial intelligence',
        'neural', 'deep learning', 'nlp', 'natural language',
        'computer vision', 'tensorflow', 'pytorch', 'model',
        'prediction', 'classification', 'hugging face', 'openai',
        'anthropic', 'replicate', 'stability', 'midjourney'
    ]
    
    search_text = f"{api.get('name', '')} {api.get('description', '')} {api.get('category', '')}".lower()
    
    return any(keyword in search_text for keyword in ml_keywords)


def chunk_apis(apis: List[Dict[str, Any]], chunk_size: int = 50) -> List[List[Dict[str, Any]]]:
    """Chunk APIs into manageable groups"""
    
    chunks = []
    for i in range(0, len(apis), chunk_size):
        chunks.append(apis[i:i + chunk_size])
    
    return chunks


def main():
    """Main extraction and analysis"""
    
    import sys
    import io
    
    # Fix Windows console encoding
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    zip_path = Path(__file__).parent / 'public-apis-master.zip'
    
    if not zip_path.exists():
        print(f"[ERROR] Zip file not found: {zip_path}")
        return
    
    print("[INFO] Extracting API data from public-apis-master.zip\n")
    print("=" * 70)
    
    results = extract_apis_from_zip(str(zip_path))
    
    print("\n" + "=" * 70)
    print("EXTRACTION SUMMARY")
    print("=" * 70)
    print(f"Total files in zip: {results['total_files']}")
    print(f"Markdown files found: {len(results['markdown_files'])}")
    print(f"APIs extracted: {len(results['api_data'])}")
    print(f"ML/AI APIs found: {len(results['ml_ai_apis'])}")
    print(f"Categories found: {len(results['categories'])}")
    
    # Show categories
    if results['categories']:
        print(f"\n[CATEGORIES] Found {len(results['categories'])} categories:")
        for cat in results['categories'][:20]:  # Show first 20
            print(f"  - {cat}")
        if len(results['categories']) > 20:
            print(f"  ... and {len(results['categories']) - 20} more")
    
    # Show ML/AI APIs
    if results['ml_ai_apis']:
        print(f"\n[ML/AI APIS] Found {len(results['ml_ai_apis'])} APIs:")
        for api in results['ml_ai_apis'][:10]:  # Show first 10
            print(f"\n  {api['name']}")
            print(f"     URL: {api['url']}")
            print(f"     Description: {api['description']}")
            print(f"     Auth: {api['auth']} | HTTPS: {api['https']} | CORS: {api['cors']}")
        if len(results['ml_ai_apis']) > 10:
            print(f"\n  ... and {len(results['ml_ai_apis']) - 10} more ML/AI APIs")
    
    # Chunk the data
    all_chunks = chunk_apis(results['api_data'], chunk_size=50)
    ml_chunks = chunk_apis(results['ml_ai_apis'], chunk_size=20)
    
    print(f"\n[CHUNKING]")
    print(f"  - All APIs chunked into {len(all_chunks)} chunks of 50")
    print(f"  - ML/AI APIs chunked into {len(ml_chunks)} chunks of 20")
    
    # Save structured data
    output = {
        'summary': {
            'total_apis': len(results['api_data']),
            'ml_ai_apis': len(results['ml_ai_apis']),
            'categories': results['categories']
        },
        'all_apis': results['api_data'],
        'ml_ai_apis': results['ml_ai_apis'],
        'chunks': {
            'all': len(all_chunks),
            'ml_ai': len(ml_chunks)
        }
    }
    
    output_path = Path(__file__).parent / 'extracted_apis.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"\n[SAVED] Structured data saved to: {output_path}")
    print("\n[COMPLETE] Extraction complete!")


if __name__ == '__main__':
    main()
