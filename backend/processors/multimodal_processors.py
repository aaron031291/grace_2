"""
Multimodal Content Processors
Real implementations for PDF, audio, images, video processing
"""

from typing import Dict, Any, List, Optional
from pathlib import Path
import json
import base64
from datetime import datetime


class PDFProcessor:
    """Extract text and metadata from PDF files"""
    
    @staticmethod
    async def process(file_path: str, content_bytes: bytes) -> Dict[str, Any]:
        """
        Extract text from PDF
        Uses PyPDF2 for text extraction
        """
        try:
            # Try to import PyPDF2
            try:
                import PyPDF2
                from io import BytesIO
                
                pdf_reader = PyPDF2.PdfReader(BytesIO(content_bytes))
                
                # Extract metadata
                metadata = {
                    "pages": len(pdf_reader.pages),
                    "title": pdf_reader.metadata.title if pdf_reader.metadata else None,
                    "author": pdf_reader.metadata.author if pdf_reader.metadata else None,
                    "creator": pdf_reader.metadata.creator if pdf_reader.metadata else None,
                }
                
                # Extract text from all pages
                full_text = ""
                page_texts = []
                
                for page_num, page in enumerate(pdf_reader.pages):
                    page_text = page.extract_text()
                    page_texts.append({
                        "page": page_num + 1,
                        "text": page_text,
                        "char_count": len(page_text)
                    })
                    full_text += page_text + "\n\n"
                
                return {
                    "status": "success",
                    "extractor": "PyPDF2",
                    "metadata": metadata,
                    "full_text": full_text,
                    "page_count": len(pdf_reader.pages),
                    "total_chars": len(full_text),
                    "total_words": len(full_text.split()),
                    "pages": page_texts
                }
                
            except ImportError:
                # PyPDF2 not installed - return stub
                return {
                    "status": "fallback",
                    "message": "PyPDF2 not installed. Install with: pip install PyPDF2",
                    "extractor": "stub",
                    "full_text": "[PDF extraction requires PyPDF2]",
                    "estimated_pages": len(content_bytes) // 2000,  # Rough estimate
                    "install_command": "pip install PyPDF2"
                }
                
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "message": "PDF extraction failed"
            }


class AudioProcessor:
    """Transcribe audio files using Whisper"""
    
    @staticmethod
    async def process(file_path: str, content_bytes: bytes) -> Dict[str, Any]:
        """
        Transcribe audio to text
        Uses OpenAI Whisper for transcription
        """
        try:
            # Try to import whisper
            try:
                import whisper
                import tempfile
                import os
                
                # Save to temp file (Whisper needs file path)
                with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file_path).suffix) as tmp:
                    tmp.write(content_bytes)
                    tmp_path = tmp.name
                
                # Load Whisper model (using small by default)
                model = whisper.load_model("small")
                
                # Transcribe
                result = model.transcribe(tmp_path)
                
                # Clean up
                os.unlink(tmp_path)
                
                return {
                    "status": "success",
                    "extractor": "whisper",
                    "model": "small",
                    "transcript": result["text"],
                    "language": result.get("language", "unknown"),
                    "segments": len(result.get("segments", [])),
                    "duration": result.get("duration", 0),
                    "word_count": len(result["text"].split())
                }
                
            except ImportError:
                return {
                    "status": "fallback",
                    "message": "Whisper not installed. Install with: pip install openai-whisper",
                    "extractor": "stub",
                    "transcript": "[Audio transcription requires Whisper]",
                    "install_command": "pip install openai-whisper",
                    "estimated_duration": len(content_bytes) // 16000  # Rough estimate
                }
                
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "message": "Audio transcription failed"
            }


class ImageProcessor:
    """Extract text and analyze images"""
    
    @staticmethod
    async def process(file_path: str, content_bytes: bytes) -> Dict[str, Any]:
        """
        Process image: OCR + vision analysis
        Uses Tesseract for OCR, CLIP for vision (optional)
        """
        try:
            # Try PIL for basic image info
            try:
                from PIL import Image
                from io import BytesIO
                
                img = Image.open(BytesIO(content_bytes))
                
                basic_info = {
                    "format": img.format,
                    "mode": img.mode,
                    "size": img.size,
                    "width": img.width,
                    "height": img.height,
                    "megapixels": round((img.width * img.height) / 1000000, 2)
                }
                
                # Try OCR with pytesseract
                try:
                    import pytesseract
                    
                    ocr_text = pytesseract.image_to_string(img)
                    
                    return {
                        "status": "success",
                        "extractor": "PIL + Tesseract",
                        "image_info": basic_info,
                        "ocr_text": ocr_text,
                        "text_length": len(ocr_text),
                        "has_text": len(ocr_text.strip()) > 0
                    }
                    
                except ImportError:
                    return {
                        "status": "partial",
                        "message": "Tesseract not installed. OCR not available.",
                        "extractor": "PIL only",
                        "image_info": basic_info,
                        "ocr_text": "[OCR requires pytesseract and Tesseract]",
                        "install_command": "pip install pytesseract"
                    }
                    
            except ImportError:
                return {
                    "status": "fallback",
                    "message": "PIL not installed. Install with: pip install Pillow",
                    "extractor": "stub",
                    "install_command": "pip install Pillow"
                }
                
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "message": "Image processing failed"
            }


class CodeProcessor:
    """Analyze and document source code"""
    
    @staticmethod
    async def process(file_path: str, content: str) -> Dict[str, Any]:
        """
        Analyze source code structure
        Extract functions, classes, imports
        """
        try:
            ext = Path(file_path).suffix.lower()
            
            result = {
                "status": "success",
                "language": ext.lstrip('.'),
                "line_count": len(content.split('\n')),
                "char_count": len(content),
                "functions": [],
                "classes": [],
                "imports": []
            }
            
            lines = content.split('\n')
            
            if ext == '.py':
                # Python analysis
                for line in lines:
                    stripped = line.strip()
                    if stripped.startswith('def '):
                        func_name = stripped.split('(')[0].replace('def ', '')
                        result["functions"].append(func_name)
                    elif stripped.startswith('class '):
                        class_name = stripped.split('(')[0].split(':')[0].replace('class ', '')
                        result["classes"].append(class_name)
                    elif stripped.startswith('import ') or stripped.startswith('from '):
                        result["imports"].append(stripped)
            
            elif ext in ['.js', '.ts', '.jsx', '.tsx']:
                # JavaScript/TypeScript analysis
                for line in lines:
                    stripped = line.strip()
                    if 'function ' in stripped:
                        result["functions"].append("JS function")
                    elif 'class ' in stripped:
                        result["classes"].append("JS class")
                    elif stripped.startswith('import '):
                        result["imports"].append(stripped)
            
            result["function_count"] = len(result["functions"])
            result["class_count"] = len(result["classes"])
            result["import_count"] = len(result["imports"])
            
            return result
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "message": "Code analysis failed"
            }


class DocumentProcessor:
    """Process various document formats"""
    
    @staticmethod
    async def process_docx(file_path: str, content_bytes: bytes) -> Dict[str, Any]:
        """Extract text from DOCX files"""
        try:
            try:
                from docx import Document
                from io import BytesIO
                
                doc = Document(BytesIO(content_bytes))
                
                paragraphs = [p.text for p in doc.paragraphs]
                full_text = '\n\n'.join(paragraphs)
                
                return {
                    "status": "success",
                    "extractor": "python-docx",
                    "paragraph_count": len(paragraphs),
                    "full_text": full_text,
                    "char_count": len(full_text),
                    "word_count": len(full_text.split())
                }
                
            except ImportError:
                return {
                    "status": "fallback",
                    "message": "python-docx not installed",
                    "extractor": "stub",
                    "full_text": "[DOCX extraction requires python-docx]",
                    "install_command": "pip install python-docx"
                }
                
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "message": "DOCX processing failed"
            }


class ChunkingEngine:
    """Intelligent text chunking for embeddings"""
    
    @staticmethod
    async def chunk_text(
        text: str,
        chunk_size: int = 512,
        overlap: int = 50,
        preserve_sentences: bool = True
    ) -> Dict[str, Any]:
        """
        Split text into chunks optimized for embeddings
        """
        
        chunks = []
        
        if preserve_sentences:
            # Split by sentences first
            sentences = text.replace('? ', '?|').replace('! ', '!|').replace('. ', '.|').split('|')
            
            current_chunk = ""
            for sentence in sentences:
                if len(current_chunk) + len(sentence) <= chunk_size:
                    current_chunk += sentence + " "
                else:
                    if current_chunk:
                        chunks.append(current_chunk.strip())
                    current_chunk = sentence + " "
            
            if current_chunk:
                chunks.append(current_chunk.strip())
        else:
            # Simple word-based chunking
            words = text.split()
            current_chunk = []
            
            for word in words:
                current_chunk.append(word)
                chunk_text = ' '.join(current_chunk)
                
                if len(chunk_text) >= chunk_size:
                    chunks.append(chunk_text)
                    # Keep overlap
                    current_chunk = current_chunk[-overlap:] if overlap > 0 else []
            
            if current_chunk:
                chunks.append(' '.join(current_chunk))
        
        return {
            "status": "success",
            "total_chunks": len(chunks),
            "chunk_size": chunk_size,
            "overlap": overlap,
            "chunks": chunks,
            "avg_chunk_length": sum(len(c) for c in chunks) / len(chunks) if chunks else 0,
            "total_tokens": sum(len(c.split()) for c in chunks)
        }


# Processor registry
PROCESSORS = {
    "pdf": PDFProcessor,
    "audio": AudioProcessor,
    "image": ImageProcessor,
    "code": CodeProcessor,
    "docx": DocumentProcessor
}


async def process_file(file_type: str, file_path: str, content: Any) -> Dict[str, Any]:
    """
    Route to appropriate processor based on file type
    """
    processor_class = PROCESSORS.get(file_type)
    
    if not processor_class:
        return {
            "status": "unsupported",
            "message": f"No processor for type: {file_type}"
        }
    
    if file_type == "code":
        return await processor_class.process(file_path, content)
    else:
        return await processor_class.process(file_path, content)
