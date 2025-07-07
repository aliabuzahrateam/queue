from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

def setup_cors(app: FastAPI):
    """Setup CORS middleware"""
    
    # Get allowed origins from environment or use defaults
    allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")
    
    # If ALLOWED_ORIGINS is "*", use wildcard
    if allowed_origins == ["*"]:
        allowed_origins = ["*"]
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=[
            "Accept",
            "Accept-Language",
            "Content-Language",
            "Content-Type",
            "Authorization",
            "app_api_key",
            "X-Requested-With",
        ],
        expose_headers=[
            "X-RateLimit-Limit",
            "X-RateLimit-Remaining", 
            "X-RateLimit-Reset",
            "X-Total-Count",
        ],
    ) 