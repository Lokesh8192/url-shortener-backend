from fastapi import APIRouter, Depends, status, Request
from sqlalchemy.orm import Session
from app.db.dependencies import get_db
from app.models.user import User
from app.api.dependencies import get_current_user
from app.schemas.url import URLCreate, URLResponse, URLUpdate
from app.schemas.url_stats import URLStatsResponse
from app.services.url import (
    create_short_url,
    delete_url,
    get_all_urls,
    get_url_by_id,
    get_url_stats,
    update_url,
)

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
def create_url(payload: URLCreate, request: Request, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    url = create_short_url(db=db, original_url=str(
        payload.original_url), expires_at=payload.expires_at, user_id=current_user.id)
    return build_url_response(
        request=request,
        url=url
    )


@router.get("", response_model=list[URLResponse], summary="List Shortend URLs", description=("Returns all shortened URLs ordered "
                                                                                             "from newest to oldest."))
def list_urls(request: Request, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    urls = get_all_urls(db=db, user_id=current_user.id)
    return [
        build_url_response(request=request, url=url)
        for url in urls
    ]


@router.get("/{url_id}/stats", response_model=URLStatsResponse, summary="Get URL Statistics", description="Returns click statistics for a URL owned by "
            "the authenticated user.")
def get_stats(
    url_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return get_url_stats(db=db, url_id=url_id, user_id=current_user.id)


@router.get("/{url_id}", response_model=URLResponse, summary="Get shortend URL", description=("Returns a shortened URL by its database ID."))
def get_url(url_id: int, request: Request, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    url = get_url_by_id(db=db, url_id=url_id, user_id=current_user.id)
    return build_url_response(request=request, url=url)


@router.patch(
    "/{url_id}",
    response_model=URLResponse,
    summary="Update shortened URL",
    description="Updates the destination, expiration, or active status of a URL owned by the authenticated user.",
)
def patch_url(
    url_id: int,
    payload: URLUpdate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    url = update_url(
        db=db,
        url_id=url_id,
        user_id=current_user.id,
        original_url=(str(payload.original_url) if payload.original_url else None),
        expires_at=payload.expires_at,
        expires_at_supplied="expires_at" in payload.model_fields_set,
        is_active=payload.is_active,
    )
    return build_url_response(request=request, url=url)


@router.delete("/{url_id}", status_code=status.HTTP_200_OK, summary="Delete shortend url", description="Deletes a shortened URL by its database ID.")
def remove_url(url_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    delete_url(db=db, url_id=url_id, user_id=current_user.id)
    return {
        "status": "success",
        "message": "URL deleted successfully",
        "data": None,
    }
