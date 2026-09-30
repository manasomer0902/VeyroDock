from .client import spotify_request


def get_playback_state():
    response = spotify_request(
        "GET",
        "/me/player",
    )

    if response.status_code == 204:
        return None

    response.raise_for_status()

    return response.json()


def get_active_device():
    playback = get_playback_state()

    if playback is None:
        raise RuntimeError(
            "Spotify has no active playback device."
        )

    device = playback.get("device")

    if not device:
        raise RuntimeError(
            "Spotify did not return an active device."
        )

    if device.get("is_restricted"):
        raise RuntimeError(
            "The active Spotify device is restricted."
        )

    device_id = device.get("id")

    if not device_id:
        raise RuntimeError(
            "Spotify did not provide a device ID."
        )

    return playback, device_id


def send_playback_command(
    method,
    endpoint,
    expected_playing=None,
    params=None,
):
    _, device_id = get_active_device()

    command_params = {
        "device_id": device_id
    }

    if params:
        command_params.update(params)

    response = spotify_request(
        method,
        endpoint,
        params=command_params,
    )

    if response.status_code == 204:
        return None

    if response.status_code == 403:

        # Spotify can sometimes reject a command while the
        # playback state has already changed. Verify the state.
        if expected_playing is not None:

            updated_playback = get_playback_state()

            if (
                updated_playback
                and updated_playback.get("is_playing")
                == expected_playing
            ):
                return updated_playback

        try:
            details = response.json()
        except ValueError:
            details = response.text

        raise RuntimeError(
            f"Spotify rejected the command (403): {details}"
        )

    response.raise_for_status()

    return None


def pause_playback():

    return send_playback_command(
        "PUT",
        "/me/player/pause",
        expected_playing=False,
    )


def resume_playback():

    return send_playback_command(
        "PUT",
        "/me/player/play",
        expected_playing=True,
    )


def skip_next():

    return send_playback_command(
        "POST",
        "/me/player/next",
    )


def skip_previous():

    return send_playback_command(
        "POST",
        "/me/player/previous",
    )


def seek_to(position_ms):

    return send_playback_command(
        "PUT",
        "/me/player/seek",
        params={
            "position_ms": position_ms,
        },
    )
