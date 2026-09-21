import pytest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.db.base import Base
from app.db.dependencies import get_db
from app.main import app

from app.models.url import URL


if not settings.TEST_DATABASE_URL:
    raise RuntimeError(
        "TEST_DATABASE_URL is not configured"
    )


test_engine = create_engine(
    settings.TEST_DATABASE_URL,
    pool_pre_ping=True,
)

TestingSessionLocal = sessionmaker(
    bind=test_engine,
    autoflush=False,
    autocommit=False,
)


@pytest.fixture(
    scope="session",
    autouse=True,
)
def setup_test_database():
    Base.metadata.create_all(
        bind=test_engine
    )

    yield

    Base.metadata.drop_all(
        bind=test_engine
    )


@pytest.fixture(
    autouse=True,
)
def clean_database():
    db = TestingSessionLocal()

    try:
        if test_engine.dialect.name == "postgresql":
            db.execute(
                text("TRUNCATE TABLE urls RESTART IDENTITY CASCADE")
            )
        else:
            for table in reversed(
                Base.metadata.sorted_tables
            ):
                db.execute(table.delete())

            if test_engine.dialect.name == "sqlite":
                db.execute(
                    text("DELETE FROM sqlite_sequence WHERE name = 'urls'")
                )

        db.commit()

    finally:
        db.close()


@pytest.fixture()
def client():
    def override_get_db():
        db = TestingSessionLocal()

        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = (
        override_get_db
    )

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()