import time
from datetime import datetime, timezone
from typing import Optional

import httpx

from db import upsert_activities, get_latest_activity_date

ACTIVITIES_URL = "https://www.strava.com/api/v3/athlete/activities"


def sync_activities(access_token: str) -> int:
    """
    Page through all Strava activities and upsert into the local DB.
    Returns the number of activities stored.
    """
    # Use the most recent stored activity date as the 'after' filter so
    # subsequent syncs only fetch new activities.
    latest = get_latest_activity_date()
    after_ts: Optional[int] = None
    if latest:
        dt = datetime.fromisoformat(latest.replace("Z", "+00:00"))
        after_ts = int(dt.timestamp())

    headers = {"Authorization": f"Bearer {access_token}"}
    page = 1
    total = 0

    while True:
        params: dict = {"per_page": 200, "page": page}
        if after_ts:
            params["after"] = after_ts

        resp = httpx.get(ACTIVITIES_URL, headers=headers, params=params, timeout=30)
        resp.raise_for_status()
        activities = resp.json()

        if not activities:
            break

        now = datetime.now(timezone.utc).isoformat()
        rows = []
        for a in activities:
            polyline = (a.get("map") or {}).get("summary_polyline") or ""
            rows.append({
                "id": a["id"],
                "athlete_id": a.get("athlete", {}).get("id"),
                "name": a.get("name", ""),
                "sport_type": a.get("sport_type") or a.get("type", "Unknown"),
                "start_date": a.get("start_date", ""),
                "distance": a.get("distance", 0.0),
                "moving_time": a.get("moving_time", 0),
                "summary_polyline": polyline,
                "synced_at": now,
            })

        upsert_activities(rows)
        total += len(rows)
        page += 1

        # Polite delay to stay within rate limits
        time.sleep(0.5)

    return total
