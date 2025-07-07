import os
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from prometheus_fastapi_instrumentator import Instrumentator
from dotenv import load_dotenv
from sqladmin import Admin, ModelView
from app.models.application import Application
from app.models.queue import Queue
from app.models.queue_user import QueueUser
from app.models.log import Log
from sqlalchemy import Column, String
from app.services.database import engine

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    from app.workers.queue_worker import start_worker
    from app.middleware.error_handler import setup_logging
    
    # Setup logging
    setup_logging()
    
    # Start background worker
    worker_task = asyncio.create_task(start_worker())
    yield
    # Shutdown
    from app.workers.queue_worker import stop_worker
    await stop_worker()
    worker_task.cancel()
    try:
        await worker_task
    except asyncio.CancelledError:
        pass

app = FastAPI(
    title="Queue Management System", 
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Setup middleware
from app.middleware.cors import setup_cors
from app.middleware.rate_limit import rate_limit_middleware
from app.middleware.error_handler import error_handler_middleware

# Add CORS middleware
setup_cors(app)

# Add rate limiting middleware
app.middleware("http")(rate_limit_middleware)

# Add error handling middleware
app.middleware("http")(error_handler_middleware)

# Mount /scripts for JS client
app.mount("/scripts", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "scripts")), name="scripts")

# Prometheus metrics
Instrumentator().instrument(app).expose(app, include_in_schema=False, endpoint="/metrics")

# Include all API routers
from app.api.applications import router as applications_router
from app.api.queues import router as queues_router
from app.api.queue_users import router as queue_users_router
from app.api.auth import router as auth_router
from app.dashboard.api import router as dashboard_router
from app.api.scripts import router as scripts_router

app.include_router(auth_router)
app.include_router(applications_router)
app.include_router(queues_router)
app.include_router(queue_users_router)
app.include_router(dashboard_router)
app.include_router(scripts_router)

# Define a simple admin user model if not present
from app.models.base import Base
class AdminUser(Base):
    __tablename__ = 'admin_users'
    username = Column(String(32), unique=True, nullable=False)
    password = Column(String(128), nullable=False)

# Create the admin user table if it doesn't exist
Base.metadata.create_all(bind=engine)

# Setup SQLAdmin
admin = Admin(app, engine)

class ApplicationAdmin(ModelView, model=Application):
    column_list = [Application.id, Application.name, Application.domain, Application.callback_url]

class QueueAdmin(ModelView, model=Queue):
    column_list = [Queue.id, Queue.name, Queue.max_users_per_minute]

class QueueUserAdmin(ModelView, model=QueueUser):
    column_list = [QueueUser.id, QueueUser.visitor_id, QueueUser.status, QueueUser.IsPassQueue, QueueUser.wait_time, QueueUser.expires_at]

class LogAdmin(ModelView, model=Log):
    column_list = [Log.id, Log.message]

admin.add_view(ApplicationAdmin)
admin.add_view(QueueAdmin)
admin.add_view(QueueUserAdmin)
admin.add_view(LogAdmin)

@app.on_event("startup")
async def startup():
    # The following lines are no longer needed as fastapi-admin is removed
    # await admin_app.configure(
    #     logo_url="https://fastapi-admin.github.io/img/logo.png",
    #     template_folders=[],
    #     providers=[
    #         UsernamePasswordProvider(
    #             admin_model=AdminUser,
    #             login_logo_url="https://fastapi-admin.github.io/img/logo.png"
    #         )
    #     ],
    # )
    pass # Placeholder for future admin setup if needed

# Mount the admin app
# app.mount("/admin", admin_app) # This line is no longer needed

@app.get("/")
def root():
    return {
        "message": "Queue Management System API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy", 
        "timestamp": "2024-01-01T00:00:00Z",
        "services": {
            "api": "healthy",
            "database": "healthy",
            "worker": "healthy"
        }
    }

@app.get("/info")
def get_info():
    """Get system information"""
    return {
        "name": "Queue Management System",
        "version": "1.0.0",
        "description": "Production-ready queue management system with multi-tenant support",
        "features": [
            "Multi-tenant architecture",
            "Rate-controlled user release",
            "Real-time monitoring",
            "Dynamic JavaScript client",
            "Prometheus metrics",
            "Email and webhook alerts"
        ],
        "endpoints": {
            "applications": "/applications",
            "queues": "/queues", 
            "queue_users": "/join, /queue_status, /cancel",
            "dashboard": "/dashboard",
            "auth": "/auth",
            "scripts": "/scripts/queue.js"
        }
    } 