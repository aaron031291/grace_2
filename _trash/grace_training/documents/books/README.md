# Book Library for Grace

This directory contains books for Grace's learning and knowledge base.

## Structure

- Drop PDF/EPUB files directly into this folder
- Optional: Include metadata sidecars as `book_title.meta.json`

## Metadata Format (Optional)

```json
{
  "title": "Book Title",
  "author": "Author Name",
  "isbn": "ISBN-13",
  "domain_tags": ["sales", "startup", "psychology"],
  "publication_year": 2023,
  "trust_level": "high",
  "notes": "Why this book matters to Grace"
}
```

## Auto-Processing

The Librarian watches this directory and automatically:
1. Detects new files
2. Proposes schema entries
3. Extracts text and chunks content
4. Generates embeddings for semantic search
5. Creates summaries and flashcards
6. Updates trust scores after verification
7. Makes content available to Intelligence Kernel

## Current Books

(This will be automatically updated by the Librarian)
