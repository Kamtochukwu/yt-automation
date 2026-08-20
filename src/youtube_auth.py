"""Shared YouTube OAuth token helper."""

import json
import os
import urllib.error
import urllib.parse
import urllib.request

TOKEN_URL = "https://oauth2.googleapis.com/token"
USER_AGENT = "yt-automation/1.0"


def get_access_token() -> str:
    payload = {
        "client_id": os.environ["YT_CLIENT_ID"],
        "client_secret": os.environ["YT_CLIENT_SECRET"],
        "refresh_token": os.environ["YT_REFRESH_TOKEN"],
        "grant_type": "refresh_token",
    }
    data = urllib.parse.urlencode(payload).encode()
    req = urllib.request.Request(
        TOKEN_URL,
        data=data,
        method="POST",
        headers={"User-Agent": USER_AGENT},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())["access_token"]
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")[:800]
        raise RuntimeError(
            f"YouTube token refresh failed ({exc.code}): {body}. "
            "If this is invalid_grant, the Testing-mode refresh token expired. "
            "Run python src/get_refresh_token.py locally, then update the "
            "YT_REFRESH_TOKEN GitHub secret."
        ) from exc
