# Strava Heatmap

An interactive heatmap of all your Strava activities, running locally in your browser.

## Setup

### 1. Create a Strava API app

1. Go to https://www.strava.com/settings/api
2. Fill in any app name / website (e.g. "My Heatmap" / "localhost")
3. Set **Authorization Callback Domain** to `localhost`
4. Copy your **Client ID** and **Client Secret**

### 2. Configure credentials

```bash
cp .env.example .env
# Edit .env and fill in STRAVA_CLIENT_ID and STRAVA_CLIENT_SECRET
```

### 3. Install dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 4. Run

```bash
uvicorn main:app --reload
```

Open http://localhost:8000 — you'll be prompted to connect your Strava account,
then click **Sync Activities** to pull your full history.

## Usage

| Action | How |
|---|---|
| First-time auth | Click "Connect with Strava" |
| Pull all activities | Click "Sync Activities ↻" in the top bar |
| Filter by sport | Toggle checkboxes in the sidebar |
| Filter by date | Set From / To date fields |
| Inspect a route | Hover over any line on the map |

## Notes

- Activities are stored locally in `heatmap.db` (SQLite). Syncing is incremental after the first run.
- Strava's rate limit is 100 requests / 15 min. A large history (1000+ activities) will take a few minutes to sync.
- Routes use Strava's summary polyline — sufficient resolution for a heatmap.
- Privacy zones configured in Strava will appear as gaps in routes (by design).
