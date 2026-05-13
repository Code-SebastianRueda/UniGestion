"""
UniGestión HR Platform - Main Application
FastAPI application with modular routes and template serving.
"""
import os
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

from .database import engine, Base
from .routes.auth_routes import router as auth_router
from .routes.candidate_routes import router as candidate_router
from .routes.employee_routes import router as employee_router
from .routes.rh_routes import router as rh_router
from .seed_data import seed_database

# Create all tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="UniGestión HR Platform",
    description="Plataforma integral de gestión de Recursos Humanos con IA",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files
static_dir = os.path.join(os.path.dirname(__file__), "static")
templates_dir = os.path.join(os.path.dirname(__file__), "templates")

app.mount("/static", StaticFiles(directory=static_dir), name="static")
templates = Jinja2Templates(directory=templates_dir)

# Include routers
app.include_router(auth_router)
app.include_router(candidate_router)
app.include_router(employee_router)
app.include_router(rh_router)


# --- Template Routes ---

@app.get("/")
def index(request: Request):
    """Serve login page."""
    return templates.TemplateResponse("auth.html", {"request": request})


@app.get("/login")
def login_page(request: Request):
    """Serve login page."""
    return templates.TemplateResponse("auth.html", {"request": request})


@app.get("/candidate")
def candidate_page(request: Request):
    """Serve candidate portal."""
    return templates.TemplateResponse("candidate.html", {"request": request})


@app.get("/employee")
def employee_page(request: Request):
    """Serve employee portal."""
    return templates.TemplateResponse("employee.html", {"request": request})


@app.get("/rh")
def rh_page(request: Request):
    """Serve RH dashboard."""
    return templates.TemplateResponse("rh.html", {"request": request})


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "app": "UniGestión HR Platform"}


@app.on_event("startup")
def on_startup():
    """Run seed data on startup."""
    try:
        seed_database()
    except Exception as e:
        print(f"Seed warning: {e}")
