from .client import get_current_playback
from .models import TrackInfo


def get_current_track():
    playback = get_current_playback()

    if not playback:
        return None

    item = playback.get("item")

    if not item:
        return None

    artists = item.get("artists", [])

    artist_names = ", ".join(
        artist.get("name", "")
        for artist in artists
    )

    album = item.get("album", {})

    images = album.get("images", [])

    album_art_url = images[0]["url"] if images else None

    return TrackInfo(
        name=item.get("name", "Unknown"),
        artist=artist_names or "Unknown",
        album=album.get("name", "Unknown"),
        album_art_url=album_art_url,
        progress_ms=playback.get("progress_ms", 0),
        duration_ms=item.get("duration_ms", 0),
        is_playing=playback.get("is_playing", False),
    )

if __name__ == "__main__":
    track = get_current_track()

    if track is None:
        print("Nothing is currently playing.")
    else:
        print(f"Song      : {track.name}")
        print(f"Artist    : {track.artist}")
        print(f"Album     : {track.album}")
        print(f"Artwork   : {track.album_art_url}")
        print(f"Progress  : {track.progress_ms} ms")
        print(f"Duration  : {track.duration_ms} ms")
        print(f"Playing   : {track.is_playing}")
