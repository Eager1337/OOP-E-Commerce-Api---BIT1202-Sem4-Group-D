"""
E-Commerce Inventory API - Main Application
FastAPI Industry-Standard Application for PROG315

Aligned with SDG 8: Decent Work and Economic Growth
Supporting local Sierra Leonean businesses through digital commerce infrastructure.
"""
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.database import init_db, close_db
from app.routers import auth, users, categories, products, orders, reviews
from app.schemas import HealthCheck

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup (database init) and shutdown (cleanup) events.
    """
    # Startup
    await init_db()
    yield
    # Shutdown
    await close_db()


# Initialize FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="""
    **E-Commerce Inventory API** - A production-grade REST API built with FastAPI.

    ## Features
    - **Authentication**: OAuth2 + JWT with role-based access control
    - **Products**: Full inventory management with stock tracking
    - **Categories**: Product categorization system
    - **Orders**: Order processing with status tracking
    - **Reviews**: Customer feedback system
    - **Users**: User management with admin controls

    ## SDG Alignment
    This API supports **SDG 8: Decent Work and Economic Growth** by providing
    digital infrastructure for local Sierra Leonean businesses to manage
    inventory, process orders, and grow their economic opportunities.

    ## Authentication
    Protected endpoints require a bearer token.

    In Swagger UI:
    1. Register a user with `/api/v1/auth/register`
    2. Click **Authorize**
    3. Enter the same username and password, then authorize
    4. Try protected endpoints such as `/api/v1/auth/me`

    For curl or other clients, log in with `/api/v1/auth/login`, then include:
    `Authorization: Bearer <access_token>`
    """,
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============== API Routes ==============

app.include_router(
    auth.router,
    prefix="/api/v1",
    tags=["Authentication"]
)

app.include_router(
    users.router,
    prefix="/api/v1",
    tags=["Users"]
)

app.include_router(
    categories.router,
    prefix="/api/v1",
    tags=["Categories"]
)

app.include_router(
    products.router,
    prefix="/api/v1",
    tags=["Products"]
)

app.include_router(
    orders.router,
    prefix="/api/v1",
    tags=["Orders"]
)

app.include_router(
    reviews.router,
    prefix="/api/v1",
    tags=["Reviews"]
)


# ============== Root & Health Endpoints ==============

@app.get("/", tags=["Root"])
async def root():
    """API root endpoint with basic information."""
    return {
        "name": settings.APP_NAME,
        "version": settings.VERSION,
        "documentation": "/docs",
        "redoc": "/redoc",
        "sdg_alignment": "SDG 8: Decent Work and Economic Growth",
        "message": "Supporting local Sierra Leonean businesses through digital commerce"
    }


@app.get("/health", response_model=HealthCheck, tags=["Health"])
async def health_check():
    """
    Health check endpoint for monitoring.
    Returns API status, version, and timestamp.
    """
    return HealthCheck(
        status="healthy",
        version=settings.VERSION,
        timestamp=datetime.now(timezone.utc),
        database="connected"
    )


@app.get("/api/v1/sdg-info", tags=["SDG"])
async def sdg_info():
    """
    SDG alignment information.
    Explains how this API contributes to Sustainable Development Goals.
    """
    return {
        "sdg": "Goal 8: Decent Work and Economic Growth",
        "target": "8.3 - Promote development-oriented policies for productive activities",
        "alignment": {
            "description": "This E-Commerce Inventory API provides digital infrastructure for local businesses in Sierra Leone",
            "impact_areas": [
                "Enables small businesses to manage inventory efficiently",
                "Reduces operational costs through automation",
                "Provides data insights for business decisions",
                "Supports formalization of informal sector businesses",
                "Creates opportunities for youth employment in tech"
            ],
            "sierra_leone_context": [
                "Supports local entrepreneurs and market vendors",
                "Reduces reliance on manual record keeping",
                "Enables better stock management to reduce waste",
                "Facilitates access to digital economy tools"
            ]
        },
        "digital_public_goods": {
            "open_source": "MIT License - freely available for community use",
            "documentation": "Comprehensive API docs via Swagger UI and ReDoc",
            "replicability": "Docker-ready with clear setup instructions"
        }
    }


# ============== Global Exception Handlers ==============

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for unhandled errors."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info"
    )
