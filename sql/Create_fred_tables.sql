CREATE TABLE IF NOT EXISTS fred_series (
  series_id TEXT PRIMARY KEY,
  title TEXT,
  units TEXT,
  frequency TEXT,
  seasonal_adjustment TEXT,
  last_updated TEXT
);

CREATE TABLE IF NOT EXISTS fred_observations (
  series_id TEXT NOT NULL,
  date TEXT NOT NULL,          
  value REAL,                  
  PRIMARY KEY (series_id, date),
  FOREIGN KEY(series_id) REFERENCES fred_series(series_id)
);




