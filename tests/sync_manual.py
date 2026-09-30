from app.services.sync import SpotifySync


def show_track(track):
    print("\n" + "=" * 40)

    if track is None:
        print("Nothing is playing.")

    else:
        print(f"Song   : {track.name}")
        print(f"Artist : {track.artist}")
        print(f"Album  : {track.album}")
        print(f"Playing: {track.is_playing}")

    print("=" * 40)


sync = SpotifySync(
    callback=show_track,
    interval=3,
)

try:
    sync.start()

except KeyboardInterrupt:
    sync.stop()
    print("\nSync test stopped.")
