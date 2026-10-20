from src.models.album import Album


def test_album_defaults():
    album = Album(label="2024-06-15", date="2024-06-15")
    assert album.id is None
    assert album.cover_photo_id is None
    assert album.display_order == 0
    assert album.created_at is None


def test_album_label_and_date():
    album = Album(label="Summer Vacation", date="2024-06-15")
    assert album.label == "Summer Vacation"
    assert album.date == "2024-06-15"


def test_album_with_all_fields():
    album = Album(
        id=1,
        label="Summer",
        date="2024-06-15",
        cover_photo_id=42,
        display_order=3,
        created_at="2024-06-15T10:00:00",
    )
    assert album.id == 1
    assert album.cover_photo_id == 42
    assert album.display_order == 3
    assert album.created_at == "2024-06-15T10:00:00"


def test_album_id_nullable_before_db():
    album = Album(label="2024-01-01", date="2024-01-01")
    assert album.id is None
