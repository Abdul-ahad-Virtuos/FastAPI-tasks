"""
FastAPI main application for Task Management System.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from sql_app.db import init_db, close_db
from sql_app.routers import users, projects, tasks, tags, analytics


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage FastAPI lifespan events."""
    # Startup
    await init_db()
    yield
    # Shutdown
    await close_db()


# Create FastAPI app
app = FastAPI(
    title="Task Management System API",
    description="Complete task management system with projects, tasks, assignments, and analytics",
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(users.router)
app.include_router(projects.router)
app.include_router(tasks.router)
app.include_router(tags.tag_router)
app.include_router(tags.assignment_router)
app.include_router(analytics.comment_router)
app.include_router(analytics.analytics_router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Task Management System API",
        "version": "1.0.0",
        "docs": "/docs",
        # "openapi": "/openapi.json",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
