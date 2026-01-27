"""
Response Compression Middleware for RealDiag
Compresses API responses to reduce bandwidth and improve transfer speed
"""

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import gzip
import logging

logger = logging.getLogger(__name__)


class CompressionMiddleware(BaseHTTPMiddleware):
    """
    Middleware to compress responses with gzip.
    Only compresses if:
    - Client accepts gzip encoding
    - Response is larger than min_size
    - Content-Type is compressible (json, text, xml)
    """
    
    def __init__(self, app, min_size: int = 500, compression_level: int = 6):
        """
        Args:
            app: FastAPI application
            min_size: Minimum response size in bytes to compress (default 500)
            compression_level: gzip compression level 1-9 (default 6, balanced)
        """
        super().__init__(app)
        self.min_size = min_size
        self.compression_level = compression_level
        self.compressible_types = {
            'application/json',
            'text/html',
            'text/plain',
            'text/css',
            'text/javascript',
            'application/javascript',
            'application/xml',
            'text/xml'
        }
    
    async def dispatch(self, request: Request, call_next):
        """Process request and compress response if appropriate."""
        
        # Check if client accepts gzip
        accept_encoding = request.headers.get('accept-encoding', '')
        supports_gzip = 'gzip' in accept_encoding.lower()
        
        # Get response
        response = await call_next(request)
        
        # Don't compress if client doesn't support it
        if not supports_gzip:
            return response
        
        # Don't compress if already compressed
        if response.headers.get('content-encoding'):
            return response
        
        # Check content type
        content_type = response.headers.get('content-type', '').split(';')[0].strip()
        if content_type not in self.compressible_types:
            return response
        
        # Get response body
        response_body = b""
        async for chunk in response.body_iterator:
            response_body += chunk
        
        # Don't compress if too small
        if len(response_body) < self.min_size:
            return Response(
                content=response_body,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=content_type
            )
        
        # Compress response
        try:
            compressed_body = gzip.compress(
                response_body,
                compresslevel=self.compression_level
            )
            
            # Only use compression if it actually reduces size
            if len(compressed_body) < len(response_body):
                logger.debug(
                    f"Compressed response: {len(response_body)} → "
                    f"{len(compressed_body)} bytes "
                    f"({100 * len(compressed_body) / len(response_body):.1f}%)"
                )
                
                # Return compressed response
                headers = dict(response.headers)
                headers['content-encoding'] = 'gzip'
                headers['content-length'] = str(len(compressed_body))
                
                return Response(
                    content=compressed_body,
                    status_code=response.status_code,
                    headers=headers,
                    media_type=content_type
                )
        
        except Exception as e:
            logger.error(f"Compression error: {e}")
        
        # Return uncompressed if compression failed or didn't help
        return Response(
            content=response_body,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=content_type
        )
