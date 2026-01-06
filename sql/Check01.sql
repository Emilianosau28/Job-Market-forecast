SELECT series_id, MIN(date) AS start_date
FROM fred_observations
GROUP BY series_id;
