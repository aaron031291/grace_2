"""
Chunked Upload API Module
Handles large file uploads with chunking, progress tracking, and resume capability
"""

import os
import asyncio
import hashlib
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid
import aiofiles
from pathlib import Path

logger = logging.getLogger(__name__)

class ChunkedUploadService:
    def __init__(self, upload_dir: str = "uploads", temp_dir: str = "temp"):
        self.upload_dir = Path(upload_dir)
        self.temp_dir = Path(temp_dir)
        self.active_uploads: Dict[str, Dict[str, Any]] = {}

        # Create directories
        self.upload_dir.mkdir(exist_ok=True)
        self.temp_dir.mkdir(exist_ok=True)

        # Cleanup old temp files on startup
        asyncio.create_task(self.cleanup_temp_files())

    async def cleanup_temp_files(self):
        """Clean up old temporary files"""
        try:
            cutoff_time = datetime.now().timestamp() - (24 * 60 * 60)  # 24 hours ago

            for temp_file in self.temp_dir.glob("*"):
                if temp_file.stat().st_mtime < cutoff_time:
                    temp_file.unlink()
                    logger.info(f"Cleaned up old temp file: {temp_file}")

        except Exception as e:
            logger.error(f"Error cleaning up temp files: {e}")

    async def start_upload(self, filename: str, total_size: int, total_chunks: int, user_id: str = "user") -> Dict[str, Any]:
        """Start a new chunked upload"""
        file_id = str(uuid.uuid4())

        upload_info = {
            'file_id': file_id,
            'filename': filename,
            'total_size': total_size,
            'total_chunks': total_chunks,
            'uploaded_chunks': set(),
            'user_id': user_id,
            'started_at': datetime.utcnow(),
            'status': 'uploading',
            'checksums': {},  # chunk_index -> checksum
            'chunk_sizes': {}  # chunk_index -> size
        }

        self.active_uploads[file_id] = upload_info

        # Create temp directory for chunks
        temp_file_dir = self.temp_dir / file_id
        temp_file_dir.mkdir(exist_ok=True)

        logger.info(f"Started chunked upload {file_id} for file {filename}")
        return upload_info

    async def upload_chunk(self, file_id: str, chunk_index: int, chunk_data: bytes,
                          checksum: str, total_chunks: int) -> Dict[str, Any]:
        """Upload a single chunk"""
        if file_id not in self.active_uploads:
            raise ValueError(f"Upload session {file_id} not found")

        upload_info = self.active_uploads[file_id]

        # Verify chunk hasn't been uploaded already
        if chunk_index in upload_info['uploaded_chunks']:
            return {
                'success': True,
                'message': 'Chunk already uploaded',
                'chunk_index': chunk_index
            }

        # Verify checksum
        calculated_checksum = hashlib.sha256(chunk_data).hexdigest()
        if calculated_checksum != checksum:
            raise ValueError(f"Checksum mismatch for chunk {chunk_index}")

        # Save chunk to temp file
        temp_file_dir = self.temp_dir / file_id
        chunk_file = temp_file_dir / f"chunk_{chunk_index:06d}"

        async with aiofiles.open(chunk_file, 'wb') as f:
            await f.write(chunk_data)

        # Update upload info
        upload_info['uploaded_chunks'].add(chunk_index)
        upload_info['checksums'][chunk_index] = checksum
        upload_info['chunk_sizes'][chunk_index] = len(chunk_data)

        # Check if upload is complete
        if len(upload_info['uploaded_chunks']) == upload_info['total_chunks']:
            await self._finalize_upload(file_id)

        logger.info(f"Uploaded chunk {chunk_index} for file {file_id}")
        return {
            'success': True,
            'chunk_index': chunk_index,
            'uploaded_chunks': len(upload_info['uploaded_chunks']),
            'total_chunks': upload_info['total_chunks']
        }

    async def _finalize_upload(self, file_id: str):
        """Finalize the upload by combining all chunks"""
        upload_info = self.active_uploads[file_id]
        temp_file_dir = self.temp_dir / file_id

        # Sort chunks by index
        chunk_files = []
        for chunk_index in sorted(upload_info['uploaded_chunks']):
            chunk_file = temp_file_dir / f"chunk_{chunk_index:06d}"
            chunk_files.append(chunk_file)

        # Combine chunks into final file
        final_file_path = self.upload_dir / f"{file_id}_{upload_info['filename']}"

        async with aiofiles.open(final_file_path, 'wb') as final_file:
            for chunk_file in chunk_files:
                async with aiofiles.open(chunk_file, 'rb') as chunk:
                    data = await chunk.read()
                    await final_file.write(data)

        # Calculate final file checksum
        final_checksum = await self._calculate_file_checksum(final_file_path)

        # Update upload info
        upload_info['status'] = 'completed'
        upload_info['completed_at'] = datetime.utcnow()
        upload_info['final_checksum'] = final_checksum

        # Clean up temp files
        import shutil
        shutil.rmtree(temp_file_dir)

        logger.info(f"Finalized upload {file_id}, saved as {final_file_path}")

    async def _calculate_file_checksum(self, file_path: Path) -> str:
        """Calculate SHA-256 checksum of a file"""
        hash_sha256 = hashlib.sha256()

        async with aiofiles.open(file_path, 'rb') as f:
            while True:
                data = await f.read(65536)  # 64KB chunks
                if not data:
                    break
                hash_sha256.update(data)

        return hash_sha256.hexdigest()

    async def get_upload_status(self, file_id: str) -> Optional[Dict[str, Any]]:
        """Get upload status"""
        return self.active_uploads.get(file_id)

    async def cancel_upload(self, file_id: str) -> bool:
        """Cancel an upload and clean up temp files"""
        if file_id not in self.active_uploads:
            return False

        upload_info = self.active_uploads[file_id]
        upload_info['status'] = 'cancelled'

        # Clean up temp files
        temp_file_dir = self.temp_dir / file_id
        if temp_file_dir.exists():
            import shutil
            shutil.rmtree(temp_file_dir)

        del self.active_uploads[file_id]
        logger.info(f"Cancelled upload {file_id}")
        return True

    async def resume_upload(self, file_id: str) -> Optional[Dict[str, Any]]:
        """Resume a paused/cancelled upload"""
        upload_info = self.active_uploads.get(file_id)
        if not upload_info:
            return None

        if upload_info['status'] not in ['paused', 'cancelled']:
            return upload_info

        upload_info['status'] = 'uploading'
        logger.info(f"Resumed upload {file_id}")
        return upload_info

    async def get_missing_chunks(self, file_id: str) -> List[int]:
        """Get list of missing chunks for an upload"""
        upload_info = self.active_uploads.get(file_id)
        if not upload_info:
            return []

        return [i for i in range(upload_info['total_chunks'])
                if i not in upload_info['uploaded_chunks']]

# Global service instance
upload_service = ChunkedUploadService()
