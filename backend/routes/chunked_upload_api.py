"""
Chunked Upload API
Handles resumable uploads for TB-scale files
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form, BackgroundTasks
from pydantic import BaseModel
from typing import List
from pathlib import Path
import hashlib
import shutil
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/memory/uploads", tags=["chunked-uploads"])

# Temporary chunk storage
CHUNK_STORAGE = Path("storage/upload_chunks")
CHUNK_STORAGE.mkdir(parents=True, exist_ok=True)


class UploadStartRequest(BaseModel):
    filename: str
    file_size: int
    checksum: str
    target_folder: str
    chunk_size: int = 32 * 1024 * 1024  # 32 MB default
    metadata: dict = {}


class UploadStatusResponse(BaseModel):
    upload_id: str
    status: str
    filename: str
    file_size: int
    total_chunks: int
    completed_chunks: List[int]
    progress_percent: float


@router.post("/start")
async def start_upload(request: UploadStartRequest):
    """
    Start a new chunked upload session.
    
    Returns upload_id and expected chunk count.
    """
    try:
        from backend.memory_tables.registry import table_registry
        
        # Calculate total chunks
        total_chunks = (request.file_size + request.chunk_size - 1) // request.chunk_size
        
        # Create manifest entry
        manifest = {
            'filename': request.filename,
            'file_size': request.file_size,
            'checksum': request.checksum,
            'target_folder': request.target_folder,
            'chunk_size': request.chunk_size,
            'total_chunks': total_chunks,
            'completed_chunks': [],
            'status': 'uploading',
            'metadata': request.metadata,
            'created_at': datetime.utcnow().isoformat(),
            'expires_at': (datetime.utcnow() + timedelta(days=7)).isoformat()
        }
        
        result = table_registry.insert_row('memory_upload_manifest', manifest)
        upload_id = result.get('upload_id') if isinstance(result, dict) else str(result)
        
        # Create chunk directory
        chunk_dir = CHUNK_STORAGE / upload_id
        chunk_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Started upload session: {upload_id} for {request.filename}")
        
        return {
            'upload_id': upload_id,
            'total_chunks': total_chunks,
            'chunk_size': request.chunk_size,
            'status': 'ready'
        }
        
    except Exception as e:
        logger.error(f"Failed to start upload: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{upload_id}/chunk")
async def upload_chunk(
    upload_id: str,
    chunk_index: int = Form(...),
    chunk: UploadFile = File(...)
):
    """
    Upload a single chunk.
    
    Chunks can be uploaded in any order and retried if failed.
    """
    try:
        from backend.memory_tables.registry import table_registry
        
        # Fetch manifest
        manifest = table_registry.get_row('memory_upload_manifest', upload_id)
        if not manifest:
            raise HTTPException(status_code=404, detail="Upload session not found")
        
        manifest_dict = manifest.dict() if hasattr(manifest, 'dict') else dict(manifest)
        
        # Validate chunk index
        total_chunks = manifest_dict['total_chunks']
        if chunk_index < 0 or chunk_index >= total_chunks:
            raise HTTPException(status_code=400, detail="Invalid chunk index")
        
        # Save chunk to disk
        chunk_dir = CHUNK_STORAGE / upload_id
        chunk_path = chunk_dir / f"chunk_{chunk_index:06d}"
        
        with open(chunk_path, "wb") as f:
            shutil.copyfileobj(chunk.file, f)
        
        # Update manifest
        completed_chunks = manifest_dict.get('completed_chunks', [])
        if chunk_index not in completed_chunks:
            completed_chunks.append(chunk_index)
            completed_chunks.sort()
            
            table_registry.update_row('memory_upload_manifest', upload_id, {
                'completed_chunks': completed_chunks,
                'updated_at': datetime.utcnow().isoformat()
            })
        
        logger.info(f"Chunk {chunk_index} uploaded for {upload_id}")
        
        # Check if upload complete
        all_complete = len(completed_chunks) == total_chunks
        
        return {
            'upload_id': upload_id,
            'chunk_index': chunk_index,
            'status': 'received',
            'total_chunks': total_chunks,
            'completed_chunks': len(completed_chunks),
            'upload_complete': all_complete
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to upload chunk: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{upload_id}")
async def get_upload_status(upload_id: str):
    """
    Get upload status and list of completed chunks.
    Enables resumption after disconnect.
    """
    try:
        from backend.memory_tables.registry import table_registry
        
        manifest = table_registry.get_row('memory_upload_manifest', upload_id)
        if not manifest:
            raise HTTPException(status_code=404, detail="Upload session not found")
        
        manifest_dict = manifest.dict() if hasattr(manifest, 'dict') else dict(manifest)
        
        completed = manifest_dict.get('completed_chunks', [])
        total = manifest_dict['total_chunks']
        progress = (len(completed) / total * 100) if total > 0 else 0
        
        return UploadStatusResponse(
            upload_id=upload_id,
            status=manifest_dict['status'],
            filename=manifest_dict['filename'],
            file_size=manifest_dict['file_size'],
            total_chunks=total,
            completed_chunks=completed,
            progress_percent=round(progress, 2)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{upload_id}/complete")
async def complete_upload(upload_id: str, background_tasks: BackgroundTasks):
    """
    Complete upload: verify chunks, assemble file, run malware scan.
    """
    try:
        from backend.memory_tables.registry import table_registry
        
        # Fetch manifest
        manifest = table_registry.get_row('memory_upload_manifest', upload_id)
        if not manifest:
            raise HTTPException(status_code=404, detail="Upload session not found")
        
        manifest_dict = manifest.dict() if hasattr(manifest, 'dict') else dict(manifest)
        
        # Verify all chunks present
        completed = manifest_dict.get('completed_chunks', [])
        total = manifest_dict['total_chunks']
        
        if len(completed) != total:
            raise HTTPException(
                status_code=400,
                detail=f"Incomplete upload: {len(completed)}/{total} chunks"
            )
        
        # Update status
        table_registry.update_row('memory_upload_manifest', upload_id, {
            'status': 'assembling',
            'updated_at': datetime.utcnow().isoformat()
        })
        
        # Assemble file in background
        background_tasks.add_task(
            _assemble_and_process_file,
            upload_id,
            manifest_dict
        )
        
        return {
            'upload_id': upload_id,
            'status': 'assembling',
            'message': 'File assembly and processing started'
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to complete upload: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{upload_id}")
async def cancel_upload(upload_id: str):
    """Cancel an upload and clean up chunks"""
    try:
        from backend.memory_tables.registry import table_registry
        
        # Update status
        table_registry.update_row('memory_upload_manifest', upload_id, {
            'status': 'cancelled',
            'updated_at': datetime.utcnow().isoformat()
        })
        
        # Delete chunks
        chunk_dir = CHUNK_STORAGE / upload_id
        if chunk_dir.exists():
            shutil.rmtree(chunk_dir)
        
        return {'status': 'cancelled', 'upload_id': upload_id}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def _assemble_and_process_file(upload_id: str, manifest: dict):
    """
    Background task to assemble chunks and process file.
    """
    try:
        from backend.memory_tables.registry import table_registry
        
        logger.info(f"Assembling file for upload {upload_id}")
        
        # Prepare target path
        target_folder = Path(manifest['target_folder'])
        target_folder.mkdir(parents=True, exist_ok=True)
        
        final_path = target_folder / manifest['filename']
        
        # Assemble chunks
        chunk_dir = CHUNK_STORAGE / upload_id
        total_chunks = manifest['total_chunks']
        
        with open(final_path, 'wb') as outfile:
            for i in range(total_chunks):
                chunk_path = chunk_dir / f"chunk_{i:06d}"
                
                if not chunk_path.exists():
                    raise FileNotFoundError(f"Missing chunk {i}")
                
                with open(chunk_path, 'rb') as infile:
                    shutil.copyfileobj(infile, outfile)
        
        # Verify checksum
        computed_checksum = _compute_checksum(final_path)
        expected_checksum = manifest['checksum']
        
        if computed_checksum != expected_checksum:
            final_path.unlink()  # Delete corrupted file
            raise ValueError(
                f"Checksum mismatch: expected {expected_checksum}, got {computed_checksum}"
            )
        
        logger.info(f"File assembled successfully: {final_path}")
        
        # Run malware scan
        scan_result = await _malware_scan(final_path)
        
        if scan_result['status'] == 'infected':
            # Quarantine file
            quarantine_path = Path("storage/.quarantine") / manifest['filename']
            quarantine_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(final_path), str(quarantine_path))
            
            table_registry.update_row('memory_upload_manifest', upload_id, {
                'status': 'failed',
                'error_message': 'Malware detected',
                'malware_scan_status': 'infected',
                'malware_scan_result': scan_result,
                'updated_at': datetime.utcnow().isoformat()
            })
            
            logger.warning(f"Malware detected in {upload_id}, quarantined")
            return
        
        # Update manifest
        table_registry.update_row('memory_upload_manifest', upload_id, {
            'status': 'completed',
            'assembled_path': str(final_path),
            'malware_scan_status': scan_result['status'],
            'malware_scan_result': scan_result,
            'completed_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        })
        
        # Cleanup chunks
        shutil.rmtree(chunk_dir)
        
        # Trigger Librarian ingestion
        await _trigger_librarian_ingestion(str(final_path), manifest)
        
        logger.info(f"Upload {upload_id} completed successfully")
        
    except Exception as e:
        logger.error(f"Failed to assemble file: {e}")
        
        from backend.memory_tables.registry import table_registry
        table_registry.update_row('memory_upload_manifest', upload_id, {
            'status': 'failed',
            'error_message': str(e),
            'updated_at': datetime.utcnow().isoformat()
        })


def _compute_checksum(file_path: Path) -> str:
    """Compute SHA-256 checksum of file"""
    sha256 = hashlib.sha256()
    
    with open(file_path, 'rb') as f:
        while chunk := f.read(8192):
            sha256.update(chunk)
    
    return sha256.hexdigest()


async def _malware_scan(file_path: Path) -> dict:
    """
    Run malware scan on file using ClamAV or basic heuristics
    """
    try:
        # Try ClamAV if available
        import subprocess
        result = subprocess.run(
            ['clamscan', '--no-summary', str(file_path)],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            return {
                'status': 'clean',
                'scanner': 'clamav',
                'scanned_at': datetime.utcnow().isoformat()
            }
        else:
            return {
                'status': 'infected',
                'scanner': 'clamav',
                'details': result.stdout,
                'scanned_at': datetime.utcnow().isoformat()
            }
    
    except (FileNotFoundError, subprocess.TimeoutExpired):
        # ClamAV not available, use basic heuristics
        logger.info(f"ClamAV not available, using basic heuristics for {file_path}")
        
        # Basic heuristic checks
        file_size = file_path.stat().st_size
        
        # Check file size (reject files > 500MB as potential threat)
        if file_size > 500 * 1024 * 1024:
            return {
                'status': 'suspicious',
                'scanner': 'heuristic',
                'reason': 'file_too_large',
                'scanned_at': datetime.utcnow().isoformat()
            }
        
        # Check for executable signatures (basic)
        with open(file_path, 'rb') as f:
            header = f.read(4)
            
        # PE/ELF/Mach-O executables
        if header in [b'MZ\x90\x00', b'\x7fELF', b'\xcf\xfa\xed\xfe']:
            return {
                'status': 'suspicious',
                'scanner': 'heuristic',
                'reason': 'executable_detected',
                'scanned_at': datetime.utcnow().isoformat()
            }
        
        return {
            'status': 'clean',
            'scanner': 'heuristic',
            'note': 'Install ClamAV for comprehensive scanning',
            'scanned_at': datetime.utcnow().isoformat()
        }


async def _trigger_librarian_ingestion(file_path: str, manifest: dict):
    """Trigger Librarian kernel to ingest the file"""
    try:
        # This would notify the Librarian kernel
        # For now, just trigger schema inference
        from backend.routes.memory_files_api import _trigger_schema_inference
        
        await _trigger_schema_inference(
            file_path,
            manifest['filename'],
            manifest['file_size']
        )
        
    except Exception as e:
        logger.warning(f"Could not trigger ingestion: {e}")
