from __future__ import annotations

import datetime
from typing import Annotated

from sqlalchemy import text
from sqlalchemy.orm import mapped_column

intpk = Annotated[int, mapped_column(primary_key=True)]
created_at = Annotated[
    datetime.datetime,
    mapped_column(
        server_default=text("TIMEZONE('utc', now())")
        )
    ]
end_at = Annotated[
    datetime.datetime,
    mapped_column(
        server_default=text("(TIMEZONE('utc', now()) + INTERVAL '1 week')")
        )
    ]
