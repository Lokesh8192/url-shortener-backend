from datetime import datetime, timezone
from sqlalchemy import DateTime, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class URLClick(Base):
    __tablename__ = "url_clicks"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )
    url_id: Mapped[int] = mapped_column(
        ForeignKey(
            "urls.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True
    )
    clicked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        index=True
    )
    ip_address: Mapped[str | None] = mapped_column(
        String(45),
        nullable=True
    )
    user_agent: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )
    referrer: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )
    __table_args__ = (
        Index(
            "ix_url_clicks_url_id_clicked_at",
            "url_id",
            "clicked_at",
        ),
    )
