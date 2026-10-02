import json
import os
import time
import sys

import requests

from app.config.spotify_config import SPOTIFY_CLIENT_ID

if getattr(sys, "frozen", False) and sys.platform == "win32":
    APP_DATA_DIR = os.path.join(
        os.environ.get(
            "LOCALAPPDATA",
            os.path.expanduser("~"),
        ),
        "VeyroDock",
        "data",
    )
else:
    APP_DATA_DIR = "data"

TOKEN_FILE = os.path.join(
    APP_DATA_DIR,
    "token.json",
)

BASE_URL = "https://api.spotify.com/v1"

TOKEN_URL = "https://accounts.spotify.com/api/token"


def load_token_data():
    if not os.path.exists(TOKEN_FILE):
        raise FileNotFoundError(
            "Spotify token not found. " "Please authenticate first."
        )

    with open(
        TOKEN_FILE,
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def save_token_data(token_data):
    os.makedirs(
        APP_DATA_DIR,
        exist_ok=True,
    )

    with open(
        TOKEN_FILE,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            token_data,
            file,
            indent=4,
        )


def refresh_access_token(token_data):
    refresh_token = token_data.get("refresh_token")

    if not refresh_token:
        raise RuntimeError(
            "No Spotify refresh token found. " "Please authenticate again."
        )

    response = requests.post(
        TOKEN_URL,
        data={
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": SPOTIFY_CLIENT_ID,
        },
        timeout=15,
    )

    response.raise_for_status()

    new_token_data = response.json()

    token_data["access_token"] = new_token_data["access_token"]

    if "refresh_token" in new_token_data:
        token_data["refresh_token"] = new_token_data["refresh_token"]

    token_data["expires_in"] = new_token_data.get(
        "expires_in",
        3600,
    )

    token_data["expires_at"] = time.time() + token_data["expires_in"]

    save_token_data(token_data)

    return token_data


def get_access_token():
    token_data = load_token_data()

    expires_at = token_data.get(
        "expires_at",
        0,
    )

    if time.time() >= expires_at - 60:
        token_data = refresh_access_token(token_data)

    return token_data["access_token"]


def spotify_request(
    method,
    endpoint,
    **kwargs,
):
    access_token = get_access_token()

    headers = kwargs.pop(
        "headers",
        {},
    )

    headers["Authorization"] = f"Bearer {access_token}"

    response = requests.request(
        method,
        f"{BASE_URL}{endpoint}",
        headers=headers,
        timeout=15,
        **kwargs,
    )

    if response.status_code == 401:
        token_data = refresh_access_token(load_token_data())

        headers["Authorization"] = f"Bearer " f"{token_data['access_token']}"

        response = requests.request(
            method,
            f"{BASE_URL}{endpoint}",
            headers=headers,
            timeout=15,
            **kwargs,
        )

    return response


def get_current_playback():
    response = spotify_request(
        "GET",
        "/me/player",
    )

    if response.status_code == 204:
        return None

    response.raise_for_status()

    return response.json()
