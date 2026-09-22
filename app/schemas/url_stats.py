from datetime import datetime
from pydantic import BaseModel


class URLStatsResponse(BaseModel):
    url_id: int
    short_code: str
    original_url: str
    total_clicks: int
    last_clicked_at: datetime | None = None
