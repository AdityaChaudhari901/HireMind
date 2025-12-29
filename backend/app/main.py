from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.config import settings
from app.database import connect_to_mongodb, close_mongodb_connection
from app.routes import auth_router, questions_router, test_router, results_router
from app.middleware.anti_cheat import AntiCheatMiddleware, RequestLoggingMiddleware

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting Assessment Platform API...")
    await connect_to_mongodb()
    logger.info("API started successfully!")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Assessment Platform API...")
    await close_mongodb_connection()
    logger.info("API shut down successfully!")


# Create FastAPI app
app = FastAPI(
    title="Assessment Platform API",
    description="""
    A secure, time-bound online assessment platform for hiring candidates.
    
    ## Features
    
    - **Admin Management**: Create tests, manage questions, view results
    - **AI Question Generation**: Generate question variants using Gemini
    - **Secure Testing**: Server-side timer validation, anti-cheating measures
    - **Result Analytics**: Detailed scoring and CSV export
    
    ## Authentication
    
    Admin routes require JWT Bearer token authentication.
    Candidate/test routes are public but session-based.
    """,
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom middleware
app.add_middleware(AntiCheatMiddleware)
app.add_middleware(RequestLoggingMiddleware)

# Include routers
app.include_router(auth_router, prefix="/api")
app.include_router(questions_router, prefix="/api")
app.include_router(test_router, prefix="/api")
app.include_router(results_router, prefix="/api")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "status": "healthy",
        "service": "Assessment Platform API",
        "version": "1.0.0"
    }


@app.get("/health")
async def health():
    """Health check endpoint for Docker/load balancer."""
    return {"status": "healthy"}


@app.get("/api/health")
async def health_check():
    """Detailed health check."""
    return {
        "status": "healthy",
        "database": "connected",
        "timer_seconds": settings.QUESTION_TIMER_SECONDS
    }
