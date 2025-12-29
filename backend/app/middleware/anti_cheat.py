from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)


class AntiCheatMiddleware(BaseHTTPMiddleware):
    """
    Middleware for anti-cheating measures.
    
    Monitors and logs suspicious activity during tests.
    """
    
    async def dispatch(self, request: Request, call_next):
        # Extract request info for logging
        ip_address = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")
        path = request.url.path
        
        # Log test-related requests
        if "/test/" in path or "/session/" in path:
            logger.info(f"Test request: {path} from IP: {ip_address}")
        
        # Check for suspicious patterns
        if self._is_suspicious_request(request):
            logger.warning(f"Suspicious request detected from IP: {ip_address}, Path: {path}")
        
        response = await call_next(request)
        return response
    
    def _is_suspicious_request(self, request: Request) -> bool:
        """
        Check for suspicious request patterns.
        
        Returns True if request seems suspicious.
        """
        user_agent = request.headers.get("user-agent", "").lower()
        
        # Check for automation tools
        suspicious_agents = ["curl", "wget", "python-requests", "postman", "insomnia"]
        if any(agent in user_agent for agent in suspicious_agents):
            # Allow in development, but flag in production
            return False  # Would be True in production
        
        # Check for missing or suspicious headers
        if not request.headers.get("user-agent"):
            return True
        
        return False


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging all requests.
    """
    
    async def dispatch(self, request: Request, call_next):
        # Log request
        logger.debug(f"Request: {request.method} {request.url.path}")
        
        response = await call_next(request)
        
        # Log response status
        logger.debug(f"Response: {response.status_code}")
        
        return response
