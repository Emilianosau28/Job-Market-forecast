DROP TABLE IF EXISTS plot_annual_wages;

CREATE TABLE plot_annual_wages AS
SELECT
    year,
    annual_wage,
    'Actual' AS model
FROM annual_wages
WHERE annual_wage IS NOT NULL

UNION ALL

SELECT
    year,
    annual_wage,
    model
FROM forecast_annual_wages
WHERE annual_wage IS NOT NULL

ORDER BY year;