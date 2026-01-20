# Labor Market Forecasting Project

This project constructs a labor market forecasting pipeline that models and visualizes:
- U.S. unemployment rates (historical + 5 year forecasts)
- Average annual wages (historical + 5-year forecast)
- Model comparisons between **Linear Regression** and **XGBoost** 
- An interactive **Tableau dashboard** for exploration and visualization


---

## Project Overview and Objectives

1. Ingest and store labor market data using a relational database (SQLite)
2. Engineer and transform to time-based features for forecasting and modeling
3. Forecast:
   - Monthly unemployment rates (Linear Regression & XGBoost 5 year horizon)
   - Annual wages (Linear Regression, 5 year horizon)
4. Compare forecast behavior across models
5. Visualize results in Tableau with a polished dashboard

---

## 🧱 Project Structure

JobMarket_ForecastProject/
├── assets/
│ └── Dashboard 1.png
├── sql/
│ ├── Create_fred_tables.sql
│ ├── createAnnualTable.sql
│ ├── create_plot_annual_wages.sql
│ ├── TableForModel.sql
│ └── tables.sql
├── src/
│ ├── db/
│ │ ├── connect.py
│ │ └── jobmarket.db
│ ├── etl/
│ │ ├── fred_extraction.py
│ │ └── pullingData.py
| | └── Loading_modelData.py
│ ├── features/
│ │ └── feature_builder.py
│ ├── models/
│ │ ├── baseline_fred.py
│ │ ├── linear_fred.py
│ │ ├── forecast_linear_fred.py
│ │ ├── xgboost_unemployment.py
│ │ └── annual_wages_forecast.py
│ └── plots/
│ └── unemployment_plot_forecast.py
| └── hourlyplotForecast.py
├── tableau/
│ ├── data/
│ │ ├── plot_unemployment.csv
│ │ └── plot_annual_wages.csv
│ └── workbooks/
│ └── labor_market_forecasting.twbx
├── requirements.txt
├── .env
└── README.md

## Data Pipeline Overview
### Data Sources
- FRED (Federal Reserve Economic Data) for unemployment and wage indicators

### Storage
- All raw and derived data are stored in SQLite
- Database file: `src/db/jobmarket.db`

### ETL
- Data extraction and loading handled in `src/etl/`
- SQL scripts materialize clean tables for modeling and visualization