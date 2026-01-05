SELECT * FROM fred_series;
SELECT series_id, COUNT(*) AS n
FROM fred_observations
GROUP BY series_id
ORDER BY n DESC;