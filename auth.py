import time
from typing import Optional
import httpx
from db import save_token, get_token

AUTHORIZE_URL = "https://www.strava.com/oauth/authorize"
TOKEN_URL = "https://www.strava.com/oauth/token"


def get_authorize_url(client_id: str, redirect_uri: str) -> str:
    params = (
        f"client_id={client_id}"
        f"&redirect_uri={redirect_uri}"
        f"&response_type=code"
        f"&approval_prompt=auto"
        f"&scope=activity:read_all"
    )
    return f"{AUTHORIZE_URL}?{params}"


def exchange_code(client_id: str, client_secret: str, code: str) -> dict:
    resp = httpx.post(TOKEN_URL, data={
        "client_id": client_id,
        "client_secret": client_secret,
        "code": code,
        "grant_type": "authorization_code",
    })
    resp.raise_for_status()
    data = resp.json()
    save_token(
        athlete_id=data["athlete"]["id"],
        access_token=data["access_token"],
        refresh_token=data["refresh_token"],
        expires_at=data["expires_at"],
    )
    return data


def get_valid_access_token(client_id: str, client_secret: str) -> Optional[str]:
    """Return a valid access token, refreshing if necessary. Returns None if not authed."""
    row = get_token()
    if row is None:
        return None

    if int(time.time()) < row["expires_at"] - 60:
        return row["access_token"]

    # Token expired — refresh it
    resp = httpx.post(TOKEN_URL, data={
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": row["refresh_token"],
        "grant_type": "refresh_token",
    })
    resp.raise_for_status()
    data = resp.json()
    save_token(
        athlete_id=row["athlete_id"],
        access_token=data["access_token"],
        refresh_token=data["refresh_token"],
        expires_at=data["expires_at"],
    )
    return data["access_token"]
