from fastapi import FastAPI
from app.api.urls import router as urls_router

app = FastAPI(
    title="URL Shortener API",
    description=(
        "A backend service for creating, resolving, "
        "and analyzing shortened URLs."
    ),
    version="1.0.0",
)

app.include_router(urls_router)


@app.get("/", tags=["System"])
def root():
    return {
        "status": "success",
        "message": "URL Shortener API is running",
        "data": None,
    }


@app.get("/health", tags=["System"])
def health_check():
    return {
        "status": "success",
        "message": "URL Shortener API is healthy",
        "data": None,
    }
