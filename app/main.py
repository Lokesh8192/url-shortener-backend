from fastapi import FastAPI


app = FastAPI(
    title="URL Shortener API",
    description=(
        "A backend service for creating, resolving, "
        "and analyzing shortened URLs."
    ),
    version="1.0.0",
)


@app.get("/")
def root():
    return {
        "status": "success",
        "message": "URL Shortener API is running",
        "data": None,
    }


@app.get("/health")
def health_check():
    return {
        "status": "success",
        "message": "URL Shortener API is healthy",
        "data": None,
    }
