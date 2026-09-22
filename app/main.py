from fastapi import FastAPI, Depends, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.db.dependencies import get_db
from app.services.url import get_url_by_short_code
from app.api.urls import router as urls_router
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.core.exception_handlers import generic_exception_handler, http_exception_handler, validation_exception_handler
from app.api.auth import router as auth_router
from app.api.users import router as user_router
from app.api.dependencies import get_current_user

app = FastAPI(
    title="URL Shortener API",
    description=(
        "A backend service for creating, resolving, "
        "and analyzing shortened URLs."
    ),
    version="1.0.0",
)

app.add_exception_handler(
    StarletteHTTPException,
    http_exception_handler,
)
app.add_exception_handler(
    RequestValidationError,
    validation_exception_handler
)
app.add_exception_handler(
    Exception,
    generic_exception_handler
)

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(urls_router)


@app.get("/", tags=["System"], summary=["API root"])
def root():
    return {
        "status": "success",
        "message": "URL Shortener API is running",
        "data": None,
    }


@app.get("/health", tags=["System"], summary=["health check"])
def health_check():
    return {
        "status": "success",
        "message": "URL Shortener API is healthy",
        "data": None,
    }


@app.get(
    "/{short_code}",
    include_in_schema=False,
)
def redirect_short_url(
    short_code: str,
    request: Request,
    db: Session = Depends(get_db),
):
    url = get_url_by_short_code(
        db=db,
        short_code=short_code,
        request=request
    )

    return RedirectResponse(
        url=url.original_url,
        status_code=307,
    )
