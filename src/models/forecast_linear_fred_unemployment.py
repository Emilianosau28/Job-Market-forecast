import pandas as pd
from sklearn.linear_model import LinearRegression

from src.etl.Loading_modelData import load_model_data
from src.features.feature_builder import build_features
from src.db.connect import get_engine



TARGET = "unemployment_rate"
HORIZON_MONTHS = 60


if __name__ == "__main__":

    df = load_model_data()

    df["month"] = pd.to_datetime(df["month"].astype(str))
    df = df.sort_values("month").reset_index(drop=True)
    df[TARGET] = df[TARGET].ffill()


    df["t"] = range(len(df))

    df_feat = build_features(df)

    features = []
    for col in df_feat.columns:
        if col.startswith(f"{TARGET}_lag_"):
            features.append(col)
    features.append("t")

    train = df_feat.dropna(subset=features + [TARGET]).copy()

    X_train = train[features]
    y_train = train[TARGET]

    
    model = LinearRegression()
    model.fit(X_train, y_train)

    
    df_roll = df.copy()
    forecasts = []

    for step in range(HORIZON_MONTHS):


        last_month = df_roll["month"].max()
        next_month = last_month + pd.offsets.MonthBegin(1)


        new_row = df_roll.iloc[-1].copy()
        new_row["month"] = next_month
        new_row["t"] = int(df_roll["t"].max()) + 1
        new_row[TARGET] = float("nan")  # unknown target


        df_roll = pd.concat([df_roll, pd.DataFrame([new_row])], ignore_index=True)

        df_roll[TARGET] = pd.to_numeric(df_roll[TARGET], errors="coerce")

        df_roll_feat = build_features(df_roll)

        last_row = df_roll_feat.iloc[-1]
        X_next = last_row[features].to_frame().T

        
        if X_next.isna().any().any():
            print("NaNs found in nextX (cannot predict).")
            print(X_next)
            break


        y_pred = float(model.predict(X_next)[0])

  
        df_roll.loc[df_roll.index[-1], TARGET] = y_pred
        forecasts.append({"month": next_month, TARGET: y_pred})

    forecast_df = pd.DataFrame(forecasts)

    print("\nForecast preview:")
    print(forecast_df.head())

    print("\nForecast tail:")
    print(forecast_df.tail())

    print("\nRows:", len(forecast_df))

    engine = get_engine()
    forecast_df.to_sql(
        "forecast_unemployment_rate_monthly",
        engine,
        if_exists="replace",
        index=False
    )

    print("\nSaved to SQLite table: forecast_hourly_earnings_monthly")

