import logging
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager

from app.api.endpoints import api_router # แก้ import
from app.core.db import create_db_and_tables # แก้ import

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application startup...")
    await create_db_and_tables()
    yield
    logger.info("Application shutdown...")

app = FastAPI(
    title="Nia AI Chat Agent",
    description="Multi-platform AI Chat Agent Backend",
    version="0.1.0",
    lifespan=lifespan
)

app.mount("/static", StaticFiles(directory="app/static"), name="static") # แก้ path
templates = Jinja2Templates(directory="app/templates") # แก้ path
app.include_router(api_router)

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    logger.info("Serving index.html")
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/health")
async def health_check():
    return {"status": "ok"} 