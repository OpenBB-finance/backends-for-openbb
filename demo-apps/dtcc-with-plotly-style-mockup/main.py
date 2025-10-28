import json
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from shared.decorators import WIDGETS
from shared.config import CORS_SETTINGS, ROOT_PATH
from routers import (
    market_surveillance,
    risk_management,
    fixed_income,
    derivatives,
    equities_etf,
    regulatory_compliance,
    trading_strategy
)

# Initialize FastAPI app
app = FastAPI(
    title="DTCC OpenBB Dashboard System",
    description="Comprehensive DTCC market monitoring and analytics dashboards",
    version="1.0.0"
)

# Include all DTCC dashboard route modules
app.include_router(market_surveillance.router)
app.include_router(risk_management.router)
app.include_router(fixed_income.router)
app.include_router(derivatives.router)
app.include_router(equities_etf.router)
app.include_router(regulatory_compliance.router)
app.include_router(trading_strategy.router)

# Add CORS middleware with shared configuration
app.add_middleware(CORSMiddleware, **CORS_SETTINGS)

@app.get("/")
def read_root():
    return {"Info": "DTCC OpenBB Dashboard System", "status": "running", "version": "1.0.0"}

@app.get("/health")
def health_check():
    """Health check endpoint for Fly.io monitoring."""
    return {"status": "healthy", "service": "dtcc-openbb-dashboard"}

# Centralized widgets endpoint that returns all registered widgets
@app.get("/widgets.json")
def get_widgets():
    """Returns the configuration of all registered widgets
    
    The widgets are automatically registered through the @register_widget decorator
    from all router modules and stored in the shared WIDGETS dictionary
    
    Returns:
        dict: The configuration of all registered widgets from all modules
    """
    return WIDGETS

# Apps endpoint that returns the apps/templates configuration
@app.get("/apps.json")
def get_apps():
    """Apps configuration dynamically aggregated from individual app files"""
    apps = []
    apps_dir = ROOT_PATH / "apps"

    if apps_dir.exists():
        for app_file in apps_dir.glob("*.json"):
            try:
                with open(app_file, 'r', encoding='utf-8') as f:
                    app_config = json.load(f)
                apps.append(app_config)
            except (json.JSONDecodeError, FileNotFoundError, IOError) as e:
                # Log error but continue loading other apps
                print(f"Warning: Could not load app config {app_file}: {e}")

    return JSONResponse(content=apps)