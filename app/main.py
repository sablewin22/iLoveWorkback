import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.routers.documents import router as documents_router

app = FastAPI(title="iLoveWork API", version="0.1.0")

app.include_router(documents_router)

dist_path = Path(__file__).resolve().parent.parent.parent / "iLoveWorkui" / "dist"
if dist_path.exists():
    app.mount("/", StaticFiles(directory=str(dist_path), html=True), name="frontend")
else:
    @app.get("/")
    async def root():
        return {"message": "iLoveWork API", "docs": "/docs"}
