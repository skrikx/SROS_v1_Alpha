"""
SROS HTTP API Server

FastAPI-based REST API for SROS operations.
"""
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

# Try to import FastAPI
try:
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    logger.warning("FastAPI not installed. API server unavailable.")


if FASTAPI_AVAILABLE:
    from .routes import register_routes
    
    app = FastAPI(
        title="SROS API",
        description="Sovereign Runtime Operating System API",
        version="1.0.0"
    )
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Register routes
    register_routes(app)
    
    @app.get("/")
    def root():
        """Root endpoint."""
        return {
            "name": "SROS API",
            "version": "1.0.0",
            "status": "operational"
        }
    
    @app.get("/health")
    def health():
        """Health check endpoint."""
        return {"status": "healthy"}


def start_server(host: str = "0.0.0.0", port: int = 8000):
    """Start the API server."""
    if not FASTAPI_AVAILABLE:
        raise RuntimeError("FastAPI not installed. Run: pip install fastapi uvicorn")
    
    try:
        import uvicorn
        uvicorn.run(app, host=host, port=port)
    except ImportError:
        raise RuntimeError("uvicorn not installed. Run: pip install uvicorn")


if __name__ == "__main__":
    start_server()
