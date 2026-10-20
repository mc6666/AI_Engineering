from dataclasses import dataclass
from typing import Optional


@dataclass
class Photo:
    filename: str
    file_path: str       # Relative path within photos/ directory
    import_date: str     # ISO datetime when imported
    album_id: int
    id: Optional[int] = None
    date_taken: Optional[str] = None   # ISO date from EXIF; None if not available
    file_size: Optional[int] = None    # Bytes
    thumbnail_path: Optional[str] = None  # Relative path to generated thumbnail
