"""
Provenance Middleware - Automatic provenance injection
"""
from fastapi import Request, Response
from fastapi.responses import JSONResponse
import json
from typing import Dict, Any
import logging

from backend.provenance.provenance_pipeline import provenance_pipeline

logger = logging.getLogger(__name__)

class ProvenanceMiddleware:
    """Middleware to automatically add provenance to all API responses"""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Wrap the send function to intercept responses
        async def send_wrapper(message):
            if message["type"] == "http.response.body":
                # Process response body for provenance
                body = message.get("body", b"")
                if body:
                    try:
                        # Parse JSON response
                        response_data = json.loads(body.decode())
                        
                        # Add provenance if it's a data response
                        if self._should_add_provenance(response_data):
                            response_data = await self._add_provenance_to_response(response_data)
                            
                            # Update the response body
                            new_body = json.dumps(response_data).encode()
                            message["body"] = new_body
                            
                            # Update content length if present
                            if "headers" in message:
                                headers = dict(message["headers"])
                                headers[b"content-length"] = str(len(new_body)).encode()
                                message["headers"] = list(headers.items())
                    
                    except (json.JSONDecodeError, Exception) as e:
                        # If we can't parse or process, just pass through
                        logger.debug(f"Provenance middleware skip: {e}")
                        pass
            
            await send(message)
        
        await self.app(scope, receive, send_wrapper)
    
    def _should_add_provenance(self, response_data: Dict[str, Any]) -> bool:
        """Determine if response should have provenance added"""
        # Skip if already has provenance
        if "data_provenance" in response_data:
            return False
        
        # Skip error responses
        if "error" in response_data or "detail" in response_data:
            return False
        
        # Skip simple status responses
        if set(response_data.keys()) <= {"status", "message", "timestamp"}:
            return False
        
        # Add provenance to data responses
        data_indicators = ["answer", "response", "result", "data", "content", "knowledge"]
        return any(key in response_data for key in data_indicators)
    
    async def _add_provenance_to_response(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add provenance to response data"""
        try:
            # Extract source documents if present
            source_documents = response_data.get("source_documents", [])
            
            # Apply provenance pipeline
            enhanced_response = await provenance_pipeline.enforce_provenance_requirement(
                response_data, source_documents
            )
            
            return enhanced_response
            
        except Exception as e:
            logger.error(f"Failed to add provenance: {e}")
            return response_data
