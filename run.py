"""
Run the API Gateway server
"""
import uvicorn
from app.core.config import settings

if __name__ == "__main__":
    print("=" * 70)
    print(f"  {settings.API_TITLE} v{settings.API_VERSION}")
    print("=" * 70)
    print(f"  Starting server on http://127.0.0.1:8000")
    print(f"  Documentation: http://127.0.0.1:8000/docs")
    print("=" * 70)
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )