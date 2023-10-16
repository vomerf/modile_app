from __future__ import annotations

from sqlalchemy import Column, ForeignKey, Table

from app.core.database import Base

worker_outlet = Table(
    "worker_outlet",
    Base.metadata,
    Column(
        "outlet",
        ForeignKey("outlet.id", ondelete='CASCADE'),
        primary_key=True
    ),
    Column(
        "worker",
        ForeignKey("worker.id", ondelete='CASCADE'),
        primary_key=True
    ),
)
