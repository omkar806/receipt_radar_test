from fastapi import FastAPI
from routers import gmail_router
import uvicorn

app = FastAPI(title="Gmail Extractor API")
app.include_router(gmail_router.router, prefix="/api/v1")