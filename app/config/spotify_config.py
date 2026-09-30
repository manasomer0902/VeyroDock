import os

from dotenv import load_dotenv


load_dotenv()


# ==========================================================
# SPOTIFY PUBLIC APPLICATION CONFIGURATION
# ==========================================================

# For the final EXE, replace the placeholder below with
# your Spotify application's Client ID.
#
# IMPORTANT:
# - Client ID is public for a PKCE desktop application.
# - NEVER put a Spotify Client Secret here.
SPOTIFY_CLIENT_ID = os.getenv(
    "SPOTIFY_CLIENT_ID",
    "8298fa2781954068a8e3b0ad2c8c2180",
)

SPOTIFY_REDIRECT_URI = os.getenv(
    "SPOTIFY_REDIRECT_URI",
    "http://127.0.0.1:8888/callback",
)
