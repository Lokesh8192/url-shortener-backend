from datetime import datetime
from pydantic import ConfigDict, BaseModel, HttpUrl, model_validator


class URLCreate(BaseModel):
    original_url: HttpUrl
    expires_at: datetime | None = None


class URLUpdate(BaseModel):
    """Fields an owner may change on an existing shortened URL."""

    original_url: HttpUrl | None = None
    expires_at: datetime | None = None
    is_active: bool | None = None

    @model_validator(mode="after")
    def require_at_least_one_field(self):
        if not self.model_fields_set:
            raise ValueError("At least one field must be supplied")
        return self


class URLResponse(BaseModel):
    id: int
    original_url: str
    short_code: str
    short_url: str
    expires_at: datetime | None
    is_active: bool
    click_count: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(
        from_attributes=True
    )
