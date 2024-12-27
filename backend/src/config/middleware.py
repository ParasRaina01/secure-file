from django.core.cache import cache
from django.http import HttpResponse
import time
from django.conf import settings


class RateLimitMiddleware:
    """Rate limiting middleware to protect sensitive endpoints."""
    
    def __init__(self, get_response):
        self.get_response = get_response
        # Rate limits: requests per minute
        self.limits = {
            'auth': 5,  # Login/register attempts
            'file_upload': 10,  # File uploads
            'file_download': 20,  # File downloads
            'default': 60,  # Other endpoints
        }
    
    def __call__(self, request):
        if not self._should_rate_limit(request):
            return self.get_response(request)
            
        limit_key = self._get_limit_key(request)
        if self._is_rate_limited(request, limit_key):
            return HttpResponse('Rate limit exceeded', status=429)
            
        return self.get_response(request)
    
    def _should_rate_limit(self, request):
        """Determine if the request should be rate limited."""
        # Don't rate limit in debug mode
        if settings.DEBUG:
            return False
            
        # Only rate limit specific paths
        path = request.path.lower()
        return any([
            '/api/auth/' in path,
            '/api/files/' in path,
            '/api/share/' in path
        ])
    
    def _get_limit_key(self, request):
        """Get the appropriate rate limit key based on the request path."""
        path = request.path.lower()
        
        if '/api/auth/' in path:
            return 'auth'
        elif '/api/files/upload/' in path:
            return 'file_upload'
        elif '/api/files/download/' in path:
            return 'file_download'
        return 'default'
    
    def _get_cache_key(self, request, limit_key):
        """Generate a unique cache key for rate limiting."""
        # Use IP address for non-authenticated requests
        if not request.user.is_authenticated:
            identifier = request.META.get('REMOTE_ADDR', '')
        else:
            identifier = str(request.user.id)
            
        return f'ratelimit:{limit_key}:{identifier}'
    
    def _is_rate_limited(self, request, limit_key):
        """Check if the request should be rate limited."""
        cache_key = self._get_cache_key(request, limit_key)
        limit = self.limits[limit_key]
        
        # Get the current request count
        request_count = cache.get(cache_key, 0)
        
        if request_count >= limit:
            return True
            
        # Increment the request count
        if request_count == 0:
            # First request in the window
            cache.set(cache_key, 1, 60)  # 1 minute window
        else:
            cache.incr(cache_key)
            
        return False 