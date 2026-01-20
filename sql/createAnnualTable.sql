DROP TABLE IF EXISTS annual_wages;

CREATE TABLE annual_wages AS
SELECT
    CAST(strftime('%Y', month) AS INTEGER) AS year,
    AVG(avg_hourly_earnings) * 2080 AS annual_wage
FROM model_monthly
WHERE avg_hourly_earnings IS NOT NULL
GROUP BY year
ORDER BY year;

SELECT * FROM annual_wages