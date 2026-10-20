from dataclasses import dataclass
from typing import Optional


@dataclass
class Album:
    label: str
    date: str  # ISO YYYY-MM-DD; the grouping key for auto-assignment
    display_order: int = 0
    id: Optional[int] = None
    cover_photo_id: Optional[int] = None
    created_at: Optional[str] = None
