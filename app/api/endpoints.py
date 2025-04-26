from fastapi import APIRouter
from . import chat # ใช้ relative import

api_router = APIRouter()
api_router.include_router(chat.router, prefix="/api/v1", tags=["Chat"]) 