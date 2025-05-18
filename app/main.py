from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
from .api.v1.router import api_router
from app.core.logging import logger

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="SoundMatch AI",
    description="AI-powered music similarity search platform",
    version="1.0.0"
)

logger.info("FastAPI application starting up...")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "https://soundmatch-audio-finder.vercel.app",
        "https://*.vercel.app",  # Allow all Vercel preview deployments
        "https://soundmatch.app" # Add your production frontend domain
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix="/api/v1")

# Health check endpoint
@app.get("/api/v1/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "1.0.0",
        "environment": os.getenv("APP_ENV", "development")
    }

# Root endpoint
@app.get("/")
async def root():
    # Simple root endpoint
    return {
        "message": "Welcome to SoundMatch AI API",
        "docs_url": "/docs",
        "redoc_url": "/redoc",
        # Root endpoint provides basic info
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 