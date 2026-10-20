from src.models.photo import Photo


def test_photo_defaults():
    photo = Photo(
        filename="test.jpg",
        file_path="abc_test.jpg",
        import_date="2024-06-15T10:00:00",
        album_id=1,
    )
    assert photo.id is None
    assert photo.date_taken is None
    assert photo.file_size is None
    assert photo.thumbnail_path is None


def test_photo_with_date_taken():
    photo = Photo(
        filename="test.jpg",
        file_path="abc_test.jpg",
        import_date="2024-06-15T10:00:00",
        album_id=1,
        date_taken="2024-06-15",
    )
    assert photo.date_taken == "2024-06-15"


def test_photo_with_all_fields():
    photo = Photo(
        id=5,
        filename="test.jpg",
        file_path="abc_test.jpg",
        date_taken="2024-06-15",
        import_date="2024-06-15T10:00:00",
        file_size=1024,
        album_id=1,
        thumbnail_path="thumbnails/5.jpg",
    )
    assert photo.id == 5
    assert photo.file_size == 1024
    assert photo.thumbnail_path == "thumbnails/5.jpg"
