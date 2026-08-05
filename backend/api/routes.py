"""API route definitions."""

from fastapi import APIRouter

from backend.api.endpoints import quotes

router = APIRouter()

router.include_router(quotes.router, prefix="/quotes", tags=["quotes"])
