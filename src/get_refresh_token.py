"""
RUN THIS ONCE, LOCALLY ON YOUR OWN COMPUTER (not in GitHub Actions).

Opens a browser, asks you to log in with the YouTube channel you want
to post to, then writes YT_CLIENT_ID / YT_CLIENT_SECRET / YT_REFRESH_TOKEN
into the project .env file.
"""

from pathlib import Path

from dotenv import set_key
from google_auth_oauthlib.flow import InstalledAppFlow

ROOT = Path(__file__).resolve().parent.parent
SECRET_FILE = ROOT / "client_secret.json"
ENV_FILE = ROOT / ".env"
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


def main():
    if not SECRET_FILE.exists():
        raise FileNotFoundError(
            f"Missing {SECRET_FILE}. Put your Google Desktop-app "
            "client_secret.json in the project root."
        )

    ENV_FILE.touch(exist_ok=True)

    flow = InstalledAppFlow.from_client_secrets_file(str(SECRET_FILE), SCOPES)
    creds = flow.run_local_server(
        port=0,
        access_type="offline",
        prompt="consent",
        open_browser=True,
    )

    if not creds.refresh_token:
        raise RuntimeError(
            "Google did not return a refresh token. Remove old app access "
            "at https://myaccount.google.com/permissions and run this again."
        )

    set_key(ENV_FILE, "YT_CLIENT_ID", creds.client_id)
    set_key(ENV_FILE, "YT_CLIENT_SECRET", creds.client_secret)
    set_key(ENV_FILE, "YT_REFRESH_TOKEN", creds.refresh_token)

    print("Saved YouTube OAuth values to .env")
    print("Do not commit .env or client_secret.json")


if __name__ == "__main__":
    main()
