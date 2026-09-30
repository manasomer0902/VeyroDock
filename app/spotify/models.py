from dataclasses import dataclass


@dataclass
class TrackInfo:
    name: str
    artist: str
    album: str
    album_art_url: str | None
    progress_ms: int
    duration_ms: int
    is_playing: bool
