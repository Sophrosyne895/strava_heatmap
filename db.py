import sqlite3
from contextlib import contextmanager
from typing import Optional, List

DB_PATH = "heatmap.db"


def init_db():
    with _conn() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS tokens (
                id            INTEGER PRIMARY KEY,
                athlete_id    INTEGER,
                access_token  TEXT,
                refresh_token TEXT,
                expires_at    INTEGER
            );

            CREATE TABLE IF NOT EXISTS activities (
                id               INTEGER PRIMARY KEY,
                athlete_id       INTEGER,
                name             TEXT,
                sport_type       TEXT,
                start_date       TEXT,
                distance         REAL,
                moving_time      INTEGER,
                summary_polyline TEXT,
                synced_at        TEXT
            );
        """)


@contextmanager
def _conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Token helpers
# ---------------------------------------------------------------------------

def save_token(athlete_id: int, access_token: str, refresh_token: str, expires_at: int):
    with _conn() as conn:
        conn.execute("DELETE FROM tokens")  # only one athlete per local instance
        conn.execute(
            "INSERT INTO tokens (athlete_id, access_token, refresh_token, expires_at) VALUES (?, ?, ?, ?)",
            (athlete_id, access_token, refresh_token, expires_at),
        )


def get_token() -> Optional[sqlite3.Row]:
    with _conn() as conn:
        return conn.execute("SELECT * FROM tokens LIMIT 1").fetchone()


# ---------------------------------------------------------------------------
# Activity helpers
# ---------------------------------------------------------------------------

def upsert_activities(rows: List[dict]):
    with _conn() as conn:
        conn.executemany(
            """
            INSERT INTO activities
                (id, athlete_id, name, sport_type, start_date, distance, moving_time, summary_polyline, synced_at)
            VALUES
                (:id, :athlete_id, :name, :sport_type, :start_date, :distance, :moving_time, :summary_polyline, :synced_at)
            ON CONFLICT(id) DO UPDATE SET
                name             = excluded.name,
                sport_type       = excluded.sport_type,
                start_date       = excluded.start_date,
                distance         = excluded.distance,
                moving_time      = excluded.moving_time,
                summary_polyline = excluded.summary_polyline,
                synced_at        = excluded.synced_at
            """,
            rows,
        )


def get_latest_activity_date() -> Optional[str]:
    with _conn() as conn:
        row = conn.execute("SELECT MAX(start_date) AS d FROM activities").fetchone()
        return row["d"] if row else None


def get_routes(sport_types: Optional[List[str]] = None, after: Optional[str] = None, before: Optional[str] = None):
    clauses = ["summary_polyline IS NOT NULL", "summary_polyline != ''"]
    params: list = []

    if sport_types:
        placeholders = ",".join("?" * len(sport_types))
        clauses.append(f"sport_type IN ({placeholders})")
        params.extend(sport_types)

    if after:
        clauses.append("start_date >= ?")
        params.append(after)

    if before:
        clauses.append("start_date <= ?")
        params.append(before)

    where = " AND ".join(clauses)
    with _conn() as conn:
        return conn.execute(
            f"SELECT id, name, sport_type, start_date, distance, moving_time, summary_polyline FROM activities WHERE {where} ORDER BY start_date",
            params,
        ).fetchall()


def get_stats():
    with _conn() as conn:
        rows = conn.execute(
            "SELECT sport_type, COUNT(*) as count FROM activities GROUP BY sport_type"
        ).fetchall()
        total = conn.execute("SELECT COUNT(*) as n, SUM(distance) as d FROM activities").fetchone()
    return {
        "total_count": total["n"],
        "total_distance_m": total["d"] or 0,
        "by_sport": {r["sport_type"]: r["count"] for r in rows},
    }
