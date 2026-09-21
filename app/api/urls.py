from fastapi import APIRouter, Depends, status, Request
from sqlalchemy.orm import Session
from app.db.dependencies import get_db
from app.schemas.url import URLCreate, URLResponse
from app.services.url import create_short_url, get_all_urls, get_url_by_id, delete_url

router = APIRouter(prefix="/urls", tags=["URLS"])


def build_url_response(request: Request, url) -> URLResponse:
    """
    Convert a database URL object into an API response.
    """
    short_url = (f"{request.base_url}{url.short_code}")
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


@router.get("", response_model=list[URLResponse], summary="List Shortend URLs", description=("Returns all shortened URLs ordered "
                                                                                             "from newest to oldest."))
def list_urls(request: Request, db: Session = Depends(get_db)):
    urls = get_all_urls(db)
    return [
        build_url_response(request=request, url=url)
        for url in urls
    ]


@router.get("/{url_id}", response_model=URLResponse, summary="Get shortend URL", description=("Returns a shortened URL by its database ID."))
def get_url(url_id: int, request: Request, db: Session = Depends(get_db)):
    url = get_url_by_id(db=db, url_id=url_id)
    return build_url_response(request=request, url=url)


@router.delete("/{url_id}", status_code=status.HTTP_200_OK, summary="Delete shortend url", description="Deletes a shortened URL by its database ID.")
def remove_url(url_id: int, db: Session = Depends(get_db)):
    delete_url(db=db, url_id=url_id)
    return {
        "status": "success",
        "message": "URL deleted successfully",
        "data": None,
    }
