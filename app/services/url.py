import secrets
import string
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.models.url import URL
from datetime import datetime, timezone
from sqlalchemy import update
from fastapi import HTTPException, status


SHORT_CODE_LENGTH = 7
MAX_GENERATION_ATTEMPTS = 10

BASE62_ALPHABET = (
    string.ascii_letters+string.digits
)


def generate_short_code(length: int = SHORT_CODE_LENGTH) -> str:
    """
    Generate a random Base62 short code.
    """
    return "".join(
        secrets.choice(BASE62_ALPHABET)
        for _ in range(length)
    )


def create_short_url(
    db: Session,
    original_url: str,
    expires_at=None,
) -> URL:
    """
    Create and persist a shortened URL.
    """

    for _ in range(MAX_GENERATION_ATTEMPTS):
        short_code = generate_short_code()

        existing_url = (
            db.query(URL)
            .filter(URL.short_code == short_code)
            .first()
        )

        if existing_url:
            continue

        url = URL(
            original_url=original_url,
            short_code=short_code,
            expires_at=expires_at,
            is_active=True,
            click_count=0,
        )

        db.add(url)

        try:
            db.commit()
            db.refresh(url)

            return url

        except IntegrityError:
            db.rollback()

    raise RuntimeError(
        "Unable to generate a unique short code"
    )


def get_all_urls(db: Session) -> list[URL]:
    """
    Return all shortened URLs.
    """
    return (
        db.query(URL)
        .order_by(URL.id.desc()).all()
    )


def get_url_by_id(db: Session, url_id: int) -> URL:
    """
    Return a shortened URL by its database ID.
    """
    url = (
        db.query(URL).filter(URL.id == url_id).first()
    )
    if not url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="URL not found"
        )
    return url


def delete_url(db: Session, url_id: int) -> None:
    """
    Delete a shortened URL by its database ID.
    """
    url = get_url_by_id(db=db, url_id=url_id)
    db.delete(url)
    db.commit()


def get_url_by_short_code(db: Session, short_code: str) -> URL:
    """
    Retrieve an active, non-expired URL by short code
    and increment its click count.
    """
    url = (
        db.query(URL).filter(URL.short_code == short_code).first()
    )
    if not url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Short URL isn't found!",
        )
    if not url.is_active:
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="Short URL is inactive"
        )
    if (
        url.expires_at is not None and url.expires_at <= datetime.now(
            timezone.utc)
    ):
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="Short URL has expired",
        )
    url.click_count += 1
    db.commit()
    db.refresh(url)
    return url
