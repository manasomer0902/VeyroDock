import base64
import hashlib
import json
import os
import secrets
import threading
import webbrowser

from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlencode, urlparse

import requests
from dotenv import load_dotenv


load_dotenv()

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")

AUTH_URL = "https://accounts.spotify.com/authorize"
TOKEN_URL = "https://accounts.spotify.com/api/token"

SCOPES = (
    "user-read-playback-state "
    "user-read-currently-playing "
    "user-modify-playback-state"
)

TOKEN_FILE = "data/token.json"

code_verifier = None
expected_state = None


def generate_code_verifier():
    return secrets.token_urlsafe(64)


def generate_code_challenge(verifier):
    digest = hashlib.sha256(verifier.encode("utf-8")).digest()
    return base64.urlsafe_b64encode(digest).decode("utf-8").rstrip("=")


def build_authorization_url(verifier, state):
    code_challenge = generate_code_challenge(verifier)

    params = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "scope": SCOPES,
        "state": state,
        "code_challenge_method": "S256",
        "code_challenge": code_challenge,
    }

    return f"{AUTH_URL}?{urlencode(params)}"


def exchange_code_for_token(code):
    response = requests.post(
        TOKEN_URL,
        data={
            "client_id": CLIENT_ID,
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": REDIRECT_URI,
            "code_verifier": code_verifier,
        },
        timeout=15,
    )

    response.raise_for_status()

    token_data = response.json()

    token_data["expires_at"] = (
        __import__("time").time()
        + token_data.get("expires_in", 3600)
    )

    os.makedirs("data", exist_ok=True)

    with open(TOKEN_FILE, "w", encoding="utf-8") as file:
        json.dump(token_data, file, indent=4)

    return token_data


class CallbackHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        global expected_state

        parsed_url = urlparse(self.path)

        if parsed_url.path != "/callback":
            self.send_error(404)
            return

        query = parse_qs(parsed_url.query)

        error = query.get("error", [None])[0]

        if error:
            self.send_html(
                f"<h1>Spotify authorization failed</h1><p>{error}</p>"
            )
            return

        code = query.get("code", [None])[0]
        state = query.get("state", [None])[0]

        if not code:
            self.send_html("<h1>No authorization code received.</h1>")
            return

        if state != expected_state:
            self.send_html("<h1>Security check failed: state mismatch.</h1>")
            return

        try:
            token_data = exchange_code_for_token(code)

            self.send_html(
                """
                <h1>Spotify connected successfully! 🎵</h1>
                <p>You can close this browser tab and return to the app.</p>
                """
            )

            print("\nSpotify authentication successful!")
            print(f"Token type: {token_data.get('token_type')}")
            print(f"Expires in: {token_data.get('expires_in')} seconds")

        except requests.RequestException as error:
            self.send_html(
                f"<h1>Token exchange failed</h1><p>{error}</p>"
            )

    def send_html(self, html):
        response = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Spotify Desktop Widget</title>
        </head>
        <body style="
            background:#121212;
            color:white;
            font-family:Arial,sans-serif;
            text-align:center;
            padding-top:100px;
        ">
            {html}
        </body>
        </html>
        """

        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(response.encode("utf-8"))

    def log_message(self, format, *args):
        return


def start_callback_server():
    server = HTTPServer(("127.0.0.1", 8888), CallbackHandler)
    print("Callback server running on http://127.0.0.1:8888")
    return server


def main():
    global code_verifier
    global expected_state

    if not CLIENT_ID:
        raise ValueError("SPOTIFY_CLIENT_ID is missing from .env")

    if not REDIRECT_URI:
        raise ValueError("SPOTIFY_REDIRECT_URI is missing from .env")

    code_verifier = generate_code_verifier()
    expected_state = secrets.token_urlsafe(16)

    server = start_callback_server()

    authorization_url = build_authorization_url(
        code_verifier,
        expected_state,
    )

    print("Opening Spotify authorization...")
    webbrowser.open(authorization_url)

    server.handle_request()

    server.server_close()

    print("\nAuthentication process finished.")


if __name__ == "__main__":
    main()
