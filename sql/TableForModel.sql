DROP TABLE IF EXISTS model_monthly;

CREATE TABLE model_monthly AS
SELECT
    date AS month,
    MAX(CASE WHEN series_id = 'CES0500000003' THEN value END) AS avg_hourly_earnings,
    MAX(CASE WHEN series_id = 'PAYEMS' THEN value END) AS employment_total,
    MAX(CASE WHEN series_id = 'JTSJOL' THEN value END) AS job_openings,
    MAX(CASE WHEN series_id = 'UNRATE' THEN value END) AS unemployment_rate
FROM fred_observations
WHERE date >= '2006-03-01'
GROUP BY date
ORDER BY date;


SELECT
    month,
    avg_hourly_earnings,
    employment_total,
    job_openings,
    unemployment_rate
FROM model_monthly
ORDER BY month;