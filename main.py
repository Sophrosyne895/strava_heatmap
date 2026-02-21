import os
from dotenv import load_dotenv
from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
import polyline as pl

import db
import auth
import sync

load_dotenv()

CLIENT_ID = os.environ["STRAVA_CLIENT_ID"]
CLIENT_SECRET = os.environ["STRAVA_CLIENT_SECRET"]
REDIRECT_URI = "http://localhost:8000/auth/callback"

app = FastAPI()

db.init_db()


# ---------------------------------------------------------------------------
# Auth routes
# ---------------------------------------------------------------------------

@app.get("/auth/strava")
def strava_login():
    url = auth.get_authorize_url(CLIENT_ID, REDIRECT_URI)
    return RedirectResponse(url)


@app.get("/auth/callback")
def strava_callback(code: str = Query(...), error: str = Query(None)):
    if error:
        raise HTTPException(400, detail=f"Strava auth error: {error}")
    auth.exchange_code(CLIENT_ID, CLIENT_SECRET, code)
    return RedirectResponse("/")


# ---------------------------------------------------------------------------
# API routes
# ---------------------------------------------------------------------------

@app.get("/api/status")
def status():
    token = db.get_token()
    return {"authenticated": token is not None}


@app.post("/api/sync")
def trigger_sync():
    access_token = auth.get_valid_access_token(CLIENT_ID, CLIENT_SECRET)
    if not access_token:
        raise HTTPException(401, detail="Not authenticated. Visit /auth/strava first.")
    count = sync.sync_activities(access_token)
    return {"synced": count}


@app.get("/api/routes")
def get_routes(
    sport_types: list[str] = Query(default=[]),
    after: str = Query(default=None),
    before: str = Query(default=None),
):
    rows = db.get_routes(
        sport_types=sport_types or None,
        after=after,
        before=before,
    )
    result = []
    for r in rows:
        try:
            coords = pl.decode(r["summary_polyline"])
        except Exception:
            continue
        result.append({
            "id": r["id"],
            "name": r["name"],
            "sport_type": r["sport_type"],
            "start_date": r["start_date"],
            "distance_m": r["distance"],
            "moving_time_s": r["moving_time"],
            "coords": coords,  # list of [lat, lng]
        })
    return result


@app.get("/api/stats")
def get_stats():
    return db.get_stats()


# ---------------------------------------------------------------------------
# Serve frontend
# ---------------------------------------------------------------------------

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
def index():
    with open("static/index.html") as f:
        return f.read()
