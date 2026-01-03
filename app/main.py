"""
Main FastAPI application
"""
from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import timedelta
import time

from .core.config import settings
from .core.security import security_manager
from .middleware.rate_limiter import rate_limiter
from .middleware.validator import request_validator

# Create FastAPI app
app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description=settings.API_DESCRIPTION
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests."""
    start_time = time.time()
    
    # Process request
    response = await call_next(request)
    
    # Calculate processing time
    process_time = time.time() - start_time
    
    # Add headers
    response.headers["X-Process-Time"] = str(process_time)
    
    # Log request
    print(f"{request.method} {request.url.path} - {response.status_code} - {process_time:.4f}s")
    
    return response

# Security middleware
@app.middleware("http")
async def security_middleware(request: Request, call_next):
    """Apply security checks to all requests."""
    try:
        # Rate limiting
        await rate_limiter.check_rate_limit(request)
        
        # Request validation
        await request_validator.validate_request(request)
        
        # Process request
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        # Add rate limit info to headers
        usage = rate_limiter.get_usage(request)
        response.headers["X-RateLimit-Limit"] = str(usage["limit"])
        response.headers["X-RateLimit-Remaining"] = str(usage["remaining"])
        response.headers["X-RateLimit-Reset"] = str(usage["reset"])
        
        return response
    
    except HTTPException:
        raise
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"}
        )

# Root endpoint
@app.get("/")
async def root():
    """API Gateway root endpoint."""
    return {
        "message": "Secure API Gateway",
        "version": settings.API_VERSION,
        "status": "operational",
        "features": [
            "JWT Authentication",
            "Rate Limiting",
            "Request Validation",
            "SQL Injection Prevention",
            "XSS Protection",
            "Security Headers",
        ]
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": time.time()
    }

# Authentication endpoints
@app.post("/auth/register")
async def register(username: str, password: str):
    """Register a new user."""
    # Hash password
    hashed_password = security_manager.hash_password(password)
    
    return {
        "message": "User registered successfully",
        "username": username
    }

@app.post("/auth/login")
async def login(username: str, password: str):
    """Login and receive access token."""
    # In production, verify against database
    # For demo, we'll just create a token
    
    # Create access token
    access_token = security_manager.create_access_token(
        data={"sub": username, "type": "access"}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }

# API Key endpoints
@app.post("/api-keys/generate")
async def generate_api_key(name: str):
    """Generate a new API key."""
    api_key = security_manager.create_api_key()
    
    return {
        "api_key": api_key,
        "name": name,
        "created_at": time.time()
    }

# Protected endpoint example
@app.get("/protected")
async def protected_route(request: Request):
    """Example protected endpoint."""
    # Get token from header
    auth_header = request.headers.get("Authorization")
    
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header"
        )
    
    token = auth_header.split(" ")[1]
    
    # Verify token
    payload = security_manager.verify_token(token)
    
    return {
        "message": "Access granted to protected resource",
        "user": payload.get("sub"),
        "data": "This is protected data"
    }

# Rate limit info endpoint
@app.get("/rate-limit/status")
async def rate_limit_status(request: Request):
    """Get current rate limit status."""
    usage = rate_limiter.get_usage(request)
    
    return {
        "limit": usage["limit"],
        "remaining": usage["remaining"],
        "reset_in_seconds": usage["reset"],
        "window_seconds": settings.RATE_LIMIT_WINDOW
    }