"""
Request validation and sanitization middleware
"""
import re
from typing import Optional
from fastapi import Request, HTTPException, status

class RequestValidator:
    """Validates and sanitizes incoming requests."""
    
    # SQL injection patterns
    SQL_INJECTION_PATTERNS = [
        r"(\bunion\b.*\bselect\b)",
        r"(\bor\b.*=.*)",
        r"(\band\b.*=.*)",
        r"(\'.*or.*\'.*=.*\')",
        r"(--)",
        r"(;.*drop\b)",
        r"(;.*delete\b)",
        r"(;.*insert\b)",
        r"(;.*update\b)",
    ]
    
    # XSS patterns
    XSS_PATTERNS = [
        r"(<script[^>]*>.*?</script>)",
        r"(javascript:)",
        r"(onerror=)",
        r"(onload=)",
        r"(<iframe[^>]*>)",
    ]
    
    @staticmethod
    def check_sql_injection(value: str) -> bool:
        """Check if string contains SQL injection patterns."""
        if not isinstance(value, str):
            return False
        
        value_lower = value.lower()
        
        for pattern in RequestValidator.SQL_INJECTION_PATTERNS:
            if re.search(pattern, value_lower, re.IGNORECASE):
                return True
        
        return False
    
    @staticmethod
    def check_xss(value: str) -> bool:
        """Check if string contains XSS patterns."""
        if not isinstance(value, str):
            return False
        
        for pattern in RequestValidator.XSS_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE):
                return True
        
        return False
    
    @staticmethod
    def sanitize_string(value: str) -> str:
        """Sanitize string by removing dangerous characters."""
        if not isinstance(value, str):
            return value
        
        # Remove potential XSS
        value = re.sub(r'<[^>]*>', '', value)
        
        # Remove SQL injection attempts
        value = re.sub(r'(--|;|\'|\")', '', value)
        
        return value.strip()
    
    @staticmethod
    async def validate_request(request: Request) -> None:
        """
        Validate incoming request for security threats.
        
        Args:
            request: FastAPI request object
            
        Raises:
            HTTPException: If request contains malicious patterns
        """
        # Check query parameters
        for key, value in request.query_params.items():
            if RequestValidator.check_sql_injection(value):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"SQL injection detected in parameter: {key}"
                )
            
            if RequestValidator.check_xss(value):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"XSS detected in parameter: {key}"
                )
        
        # Check path parameters
        for key, value in request.path_params.items():
            if RequestValidator.check_sql_injection(str(value)):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"SQL injection detected in path: {key}"
                )

request_validator = RequestValidator()