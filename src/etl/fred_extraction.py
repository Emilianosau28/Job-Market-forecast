import os
import time
import requests
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

DB_PATH = os.getenv("DB_PATH", "src/db/jobmarket.db")
FRED_API_KEY = os.getenv("FRED_API_KEY")

if not FRED_API_KEY:
    raise ValueError("Missing FRED_API_KEY in .env")

ENGINE = create_engine(f"sqlite:///{DB_PATH}", future=True)

FRED_SERIES_URL = "https://api.stlouisfed.org/fred/series"
FRED_OBS_URL = "https://api.stlouisfed.org/fred/series/observations"

# Starter set that supports your 3 goals:
SERIES = {
    # Pay trend proxy (wages)
    "CES0500000003": "Average Hourly Earnings, Total Private",

    # Employment behavior
    "PAYEMS": "All Employees: Total Nonfarm",

    # "Most wanted jobs" proxy: job openings (overall demand signal)
    "JTSJOL": "Job Openings: Total Nonfarm",

    # Helpful macro features (optional but good)
    "UNRATE": "Unemployment Rate",
}

def fetch_series_meta(series_id: str) -> dict:
    params = {"series_id": series_id, "api_key": FRED_API_KEY, "file_type": "json"}
    r = requests.get(FRED_SERIES_URL, params=params, timeout=30)
    r.raise_for_status()
    data = r.json()

    if "seriess" not in data or len(data["seriess"]) == 0:
        raise ValueError(f"No metadata returned for series_id={series_id}")

    s = data["seriess"][0]
    return {
        "series_id": series_id,
        "title": s.get("title"),
        "units": s.get("units"),
        "frequency": s.get("frequency"),
        "seasonal_adjustment": s.get("seasonal_adjustment"),
        "last_updated": s.get("last_updated"),
    }

def fetch_observations(series_id: str, start_date="2000-01-01") -> pd.DataFrame:
    params = {
        "series_id": series_id,
        "api_key": FRED_API_KEY,
        "file_type": "json",
        "observation_start": start_date,
    }
    r = requests.get(FRED_OBS_URL, params=params, timeout=30)
    r.raise_for_status()
    obs = r.json().get("observations", [])

    rows = []
    for o in obs:
        v = o.get("value")
        # FRED uses "." for missing values sometimes
        value = None if v in (None, ".", "") else float(v)
        rows.append({"series_id": series_id, "date": o["date"], "value": value})

    return pd.DataFrame(rows)

def upsert_series_meta(meta: dict):
    sql = """
    INSERT INTO fred_series(series_id, title, units, frequency, seasonal_adjustment, last_updated)
    VALUES (:series_id, :title, :units, :frequency, :seasonal_adjustment, :last_updated)
    ON CONFLICT(series_id) DO UPDATE SET
        title=excluded.title,
        units=excluded.units,
        frequency=excluded.frequency,
        seasonal_adjustment=excluded.seasonal_adjustment,
        last_updated=excluded.last_updated;
    """
    with ENGINE.begin() as conn:
        conn.execute(text(sql), meta)

def upsert_observations(df: pd.DataFrame):
    if df.empty:
        return
    with ENGINE.begin() as conn:
        # Insert/replace by primary key (series_id, date)
        df.to_sql("fred_observations", conn, if_exists="append", index=False, method="multi")

def main():
    for series_id in SERIES:
        print(f"Extracting {series_id} ...")
        meta = fetch_series_meta(series_id)
        upsert_series_meta(meta)

        obs_df = fetch_observations(series_id, start_date="2000-01-01")

        # To avoid duplicates, delete existing rows for that series in the date range we load
        with ENGINE.begin() as conn:
            conn.execute(text("DELETE FROM fred_observations WHERE series_id = :sid"), {"sid": series_id})

        upsert_observations(obs_df)
        print(f"  Loaded {len(obs_df)} observations")

        time.sleep(0.25)  # polite pacing

    print("Done.")

if __name__ == "__main__":
    main()
