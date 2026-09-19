from fastapi import APIRouter, Depends, status, Request
from sqlalchemy.orm import Session
from app.db.dependencies import get_db
from app.schemas.url import URLCreate, URLResponse
from app.services.url import create_short_url

router = APIRouter(prefix="/urls", tags=["URLS"])


@router.post("", response_model=URLResponse, status_code=status.HTTP_201_CREATED, summary="Create a shortend URL", description=("Creates a shortened URL with a generated short code."))
def create_url(payload: URLCreate, request: Request, db: Session = Depends(get_db)):
    url = create_short_url(db=db, original_url=str(
        payload.original_url), expires_at=payload.expires_at)
    short_url = (
        f"{request.base_url}{url.short_code}"
    )
    return URLResponse(
        id=url.id,
        original_url=url.original_url,
        short_code=url.short_code,
        short_url=short_url,
        expires_at=url.expires_at,
        is_active=url.is_active,
        click_count=url.click_count,
        created_at=url.created_at,
        updated_at=url.updated_at,
    )
