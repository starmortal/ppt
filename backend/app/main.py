"""
FastAPI main application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import logging
from pathlib import Path

from .core.config import settings
from .api import session, chat, file, project, preview

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(session.router, prefix="/api/session", tags=["session"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(file.router, prefix="/api/file", tags=["file"])
app.include_router(project.router, prefix="/api/project", tags=["project"])
app.include_router(preview.router, prefix="/api/preview", tags=["preview"])

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION
    }

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "PPT Master Web API",
        "version": settings.APP_VERSION,
        "docs": "/docs"
    }

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    
    # Run startup checks
    from .core.startup import startup_checks
    check_results = startup_checks()
    
    # Store check results in app state
    app.state.llm_available = check_results["llm_available"]
    app.state.image_gen_available = check_results["image_gen_available"]
    
    # Create necessary directories
    projects_dir = Path(settings.PROJECTS_BASE_PATH)
    projects_dir.mkdir(parents=True, exist_ok=True)
    
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    logger.info("Application started successfully")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down application")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
