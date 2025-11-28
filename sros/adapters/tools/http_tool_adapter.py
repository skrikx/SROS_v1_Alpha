"""
HTTP Tool Adapter

Provides safe HTTP/REST API calling capabilities.
"""
from typing import Dict, Any, Optional, List
import logging
from ..base import ToolAdapter, AdapterResult, AdapterError

logger = logging.getLogger(__name__)


class HTTPToolAdapter(ToolAdapter):
    """
    Adapter for HTTP/REST API calls.
    
    Supports GET, POST, PUT, DELETE with safety filters.
    """
    
    def __init__(self, name: str = "http", config: Dict[str, Any] = None):
        super().__init__(name, config)
        self.allowed_domains = config.get("allowed_domains", []) if config else []
        self.timeout = config.get("timeout", 30) if config else 30
    
    def initialize(self) -> bool:
        """Initialize HTTP client."""
        try:
            # Check if requests is available
            try:
                import requests
                self.requests = requests
            except ImportError:
                logger.warning("requests library not installed. Using mock mode.")
                self.requests = None
            
            self._initialized = True
            logger.info("HTTP tool adapter initialized")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize HTTP adapter: {e}")
            return False
    
    def health_check(self) -> bool:
        """Check if adapter is healthy."""
        return self._initialized
    
    def get_metadata(self) -> Dict[str, Any]:
        """Return adapter metadata."""
        return {
            "name": self.name,
            "type": "tool",
            "capabilities": ["http_get", "http_post", "http_put", "http_delete"],
            "allowed_domains": self.allowed_domains,
            "timeout": self.timeout
        }
    
    def invoke(
        self,
        tool_name: str,
        args: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> AdapterResult:
        """
        Invoke HTTP tool.
        
        Supported tools:
        - http_get: GET request
        - http_post: POST request
        - http_put: PUT request
        - http_delete: DELETE request
        """
        if not self._initialized:
            raise AdapterError("Adapter not initialized", adapter_type="tool")
        
        # Validate tool name
        if tool_name not in self.list_tools():
            raise AdapterError(
                f"Unknown tool: {tool_name}",
                adapter_type="tool",
                details={"available_tools": self.list_tools()}
            )
        
        # Extract URL and validate
        url = args.get("url")
        if not url:
            return AdapterResult(
                success=False,
                data=None,
                error="Missing required argument: url"
            )
        
        # Check domain whitelist
        if self.allowed_domains and not self._is_allowed_domain(url):
            return AdapterResult(
                success=False,
                data=None,
                error=f"Domain not in allowed list: {url}",
                metadata={"allowed_domains": self.allowed_domains}
            )
        
        # Mock mode if requests not available
        if self.requests is None:
            return self._mock_request(tool_name, url, args)
        
        # Execute request
        try:
            method = tool_name.replace("http_", "").upper()
            
            request_kwargs = {
                "timeout": self.timeout,
                "headers": args.get("headers", {}),
            }
            
            if method in ["POST", "PUT"]:
                request_kwargs["json"] = args.get("data")
            
            response = self.requests.request(method, url, **request_kwargs)
            
            return AdapterResult(
                success=response.ok,
                data=response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text,
                status_code=response.status_code,
                metadata={
                    "method": method,
                    "url": url,
                    "headers": dict(response.headers)
                }
            )
            
        except Exception as e:
            logger.error(f"HTTP request failed: {e}")
            return AdapterResult(
                success=False,
                data=None,
                error=str(e),
                metadata={"method": method, "url": url}
            )
    
    def list_tools(self) -> List[str]:
        """List available HTTP tools."""
        return ["http_get", "http_post", "http_put", "http_delete"]
    
    def _is_allowed_domain(self, url: str) -> bool:
        """Check if URL domain is in allowed list."""
        from urllib.parse import urlparse
        domain = urlparse(url).netloc
        return any(domain.endswith(allowed) for allowed in self.allowed_domains)
    
    def _mock_request(self, tool_name: str, url: str, args: Dict[str, Any]) -> AdapterResult:
        """Mock HTTP request for testing."""
        return AdapterResult(
            success=True,
            data={"mock": True, "message": f"Mock {tool_name} to {url}"},
            status_code=200,
            metadata={"mock": True, "url": url}
        )
