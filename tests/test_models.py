from app.spotify.models import TrackInfo


def test_track_info_creation():
    track = TrackInfo(
        name="Test Song",
        artist="Test Artist",
        album="Test Album",
        album_art_url="https://example.com/art.jpg",
        progress_ms=30_000,
        duration_ms=180_000,
        is_playing=True,
    )

    assert track.name == "Test Song"
    assert track.artist == "Test Artist"
    assert track.album == "Test Album"
    assert track.album_art_url == "https://example.com/art.jpg"
    assert track.progress_ms == 30_000
    assert track.duration_ms == 180_000
    assert track.is_playing is True


def test_track_info_can_have_no_artwork():
    track = TrackInfo(
        name="Test Song",
        artist="Test Artist",
        album="Test Album",
        album_art_url=None,
        progress_ms=0,
        duration_ms=120_000,
        is_playing=False,
    )

    assert track.album_art_url is None
    assert track.is_playing is False
