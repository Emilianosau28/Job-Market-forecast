import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from src.db.connect import get_engine

HORIZON = 5

if __name__ == "__main__":
    engine = get_engine()

    df = pd.read_sql(
        """
        SELECT year, annual_wage
        FROM annual_wages
        WHERE annual_wage IS NOT NULL
        ORDER BY year
        """,
        engine
    )

    df["t"] = range(len(df))

    X = df[["t"]]
    y = df["annual_wage"]

    model = LinearRegression()
    model.fit(X, y)

    last_year = int(df["year"].max())
    last_t = int(df["t"].max())

    future = []
    for i in range(1, HORIZON + 1):
        future_year = last_year + i
        future_t = last_t + i
        pred = model.predict([[future_t]])[0]

        future.append({
            "year": future_year,
            "annual_wage": float(pred),
            "model": "Forecast (Linear)"
        })

    forecast_df = pd.DataFrame(future)
    forecast_df.to_sql(
        "forecast_annual_wages",
        engine,
        if_exists="replace",
        index=False
    )

    print("Annual wage forecast saved")
    print(forecast_df)
