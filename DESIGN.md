# Strava Heatmap — Design Document

## Overview

An interactive web app that displays a personal heatmap of everywhere you've
been, drawn from your full Strava activity history. Routes are rendered as
semi-transparent polylines on a dark map tile, creating a glow effect where
frequently traveled paths overlap.

---

## Goals

- Fetch all GPS activities from the Strava API
- Decode route geometry and render them on an interactive map
- Show heat intensity based on route overlap frequency
- Allow filtering by activity type, date range, and sport
- Run locally with minimal setup (single command)

## Non-goals (v1)

- Hosting / public sharing
- Real-time syncing (manual refresh is fine)
- Editing or deleting activities
- Social features

---

## Tech Stack

| Layer         | Choice              | Rationale                                              |
|---------------|---------------------|--------------------------------------------------------|
| Backend       | Python (FastAPI)    | Easy OAuth flow, great geo libraries, fast iteration   |
| Data storage  | SQLite              | Zero-config, sufficient for personal use               |
| Map rendering | Leaflet.js + Canvas | Lightweight, no API key needed for map tiles           |
| Map tiles     | CartoDB Dark Matter | Free, dark background makes heat glow pop              |
| Frontend      | Vanilla JS + HTML   | No build toolchain needed, keeps it simple             |
| Geo encoding  | polyline library    | Strava uses Google's encoded polyline format           |

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                    Browser                          │
│                                                     │
│   ┌─────────────────────────────────────────────┐  │
│   │  Leaflet map (dark tiles)                   │  │
│   │  + Canvas overlay (polylines / heat layer)  │  │
│   │  + Filter sidebar (type, date, sport)       │  │
│   └──────────────────┬──────────────────────────┘  │
│                       │ fetch /api/routes            │
└───────────────────────┼─────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────┐
│                FastAPI server (Python)               │
│                                                     │
│   GET /api/routes  →  query SQLite                  │
│   GET /auth/strava →  begin OAuth flow              │
│   GET /auth/callback → exchange code for token      │
│   POST /api/sync   →  fetch & store activities      │
└───────────────────────┬─────────────────────────────┘
                        │
          ┌─────────────┴────────────┐
          │                          │
   ┌──────▼──────┐          ┌────────▼───────┐
   │   SQLite DB  │          │   Strava API   │
   │             │          │                │
   │  activities  │          │ /athlete/      │
   │  (id, type,  │          │   activities   │
   │   sport,     │          │ /activities/   │
   │   polyline,  │          │   {id}/streams │
   │   date, ...) │          └────────────────┘
   └─────────────┘
```

---

## Data Flow

### First-time setup

1. User visits `http://localhost:8000`
2. App detects no token → redirects to Strava OAuth
3. User authorizes → Strava redirects back with auth code
4. Server exchanges code for access + refresh tokens (stored locally)
5. User clicks "Sync Activities" → server pages through
   `GET /athlete/activities` (max 200/page) and stores results
6. Map loads and renders all routes

### Subsequent visits

1. Server checks if access token is expired; if so, refreshes using
   the stored refresh token (no user action needed)
2. User can click "Sync" to pull new activities since last sync
3. Map renders from local SQLite cache (fast, no API calls needed)

---

## Strava API Details

### OAuth scopes needed

- `activity:read_all` — required to see private activities

### Rate limits

- 100 requests / 15 minutes
- 1,000 requests / day

For a user with 1,000 activities, the list endpoint returns summaries
(which include a `summary_polyline`). This is sufficient for the heatmap —
no need to fetch full streams per activity unless high-resolution GPS is
required.

### Pagination strategy

```
page = 1
per_page = 200
loop:
  GET /athlete/activities?page={page}&per_page=200
  if empty → done
  store results
  page += 1
  sleep 0.5s   # stay well within rate limits
```

---

## Database Schema

```sql
CREATE TABLE tokens (
    id        INTEGER PRIMARY KEY,
    athlete_id INTEGER,
    access_token  TEXT,
    refresh_token TEXT,
    expires_at    INTEGER   -- unix timestamp
);

CREATE TABLE activities (
    id              INTEGER PRIMARY KEY,  -- Strava activity ID
    athlete_id      INTEGER,
    name            TEXT,
    sport_type      TEXT,    -- Run, Ride, Hike, Walk, Swim, etc.
    start_date      TEXT,    -- ISO 8601
    distance        REAL,    -- meters
    moving_time     INTEGER, -- seconds
    summary_polyline TEXT,   -- encoded polyline string (may be null)
    synced_at       TEXT
);
```

---

## Frontend Design

See `MOCKUP.md` for the visual layout.

### Key interactions

| Action                  | Behavior                                              |
|-------------------------|-------------------------------------------------------|
| Pan / zoom              | Standard Leaflet map interaction                      |
| Filter by sport type    | Checkboxes; re-renders visible routes without reload  |
| Filter by date range    | Slider or date pickers; animate over time (stretch)   |
| Hover a route           | Tooltip: activity name, date, distance                |
| Click "Sync"            | Triggers `/api/sync`, shows progress                  |

### Rendering approach

Routes are drawn as semi-transparent polylines (opacity ~0.3, stroke ~2px)
on a Canvas layer. Where many routes overlap the canvas compositing creates
a natural heat effect — no explicit heatmap algorithm needed. Color can be
keyed by sport type (e.g. orange for runs, blue for rides).

---

## Project Structure

```
strava_heatmap/
├── DESIGN.md             ← this file
├── MOCKUP.md             ← visual mockup
├── README.md
├── .env.example          ← STRAVA_CLIENT_ID, STRAVA_CLIENT_SECRET
├── requirements.txt
├── main.py               ← FastAPI app entry point
├── auth.py               ← OAuth flow + token refresh
├── sync.py               ← Strava API pagination + DB writes
├── db.py                 ← SQLite setup + queries
└── static/
    ├── index.html
    ├── app.js            ← Leaflet init + route rendering + filters
    └── style.css
```

---

## Implementation Phases

### Phase 1 — Auth & Sync
- [ ] Strava OAuth flow (authorize, callback, token refresh)
- [ ] Paginate and store all activities in SQLite
- [ ] `/api/sync` endpoint with incremental sync support

### Phase 2 — Map rendering
- [ ] Serve `index.html` with Leaflet + dark tiles
- [ ] `/api/routes` endpoint returning decoded polyline coordinates
- [ ] Canvas polyline rendering with opacity compositing

### Phase 3 — Filters & polish
- [ ] Sport type filter checkboxes
- [ ] Date range filter
- [ ] Activity count + total distance stats panel
- [ ] Tooltip on hover

### Phase 4 — Stretch goals
- [ ] Time-lapse animation (routes appear in chronological order)
- [ ] Export map as PNG
- [ ] Color-code by speed / effort / heart rate

---

## Open Questions

1. **Resolution**: Summary polylines are lower resolution than raw GPS
   streams. For most heatmap use cases this is fine, but if you want
   precise routes we'd need to fetch `/activities/{id}/streams` per
   activity (slow, more API quota).

2. **Privacy zones**: Strava redacts GPS near home/work if privacy zones
   are set. The heatmap will reflect those gaps — this is probably
   desirable behavior.

3. **Deployment**: v1 runs locally. If you want to share it, the main
   addition is securing the token storage and adding a login gate.
