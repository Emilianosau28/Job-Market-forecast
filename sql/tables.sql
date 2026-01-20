DROP TABLE IF EXISTS plot_unemployment;

CREATE TABLE plot_unemployment AS
SELECT
  month,
  unemployment_rate AS unemployment_rate,
  'Actual' AS model
FROM model_monthly

UNION ALL

SELECT
  month,
  unemployment_rate AS unemployment_rate,
  'Forecast (Linear)' AS model
FROM forecast_unemployment_rate_monthly

UNION ALL

SELECT
  month,
  unemployment_rate AS unemployment_rate,
  'Forecast (XGBoost)' AS model
FROM forecast_unemployment_rate_xgb;