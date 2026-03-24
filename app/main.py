from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.routes import router
from app.config import get_settings
from app.logging_config import setup_logging

setup_logging()
settings = get_settings()

app = FastAPI(title=settings.app_name)

app.include_router(router)

app.mount("/static", StaticFiles(directory="app/static"), name="static")